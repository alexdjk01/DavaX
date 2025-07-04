import oracledb
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt

from tables_structure.dim_tables import DimTables
from tables_structure.source_tables import SourceTables
from utils.insert_values_into_tables import InsertValuesIntoTables
from utils.queries import ReportQueries
from scripts.insert_fact_timesheets import main as insert_fact_table_data

if __name__ == "__main__":
    # 1) Open connection & build schema
    conn = oracledb.connect(
        user='dariusdinu',
        password='parolamea',
        dsn='localhost:1521/XEPDB1'
    )

    dim_tables    = DimTables(conn)
    source_tables = SourceTables(conn)

    dim_tables.create_tables()
    source_tables.create_tables()

    InsertValuesIntoTables.populate_dim_employees(conn.cursor())
    InsertValuesIntoTables.populate_dim_projects(conn.cursor())
    InsertValuesIntoTables.populate_dim_events(conn.cursor())

    insert_fact_table_data()

     # ─────────── Run Reports ───────────
    rq = ReportQueries(conn)

    # Example 1: Net hours for June 1–14
    print(f"========================================")
    print(f"Example 1: Net hours for June 1–14")
    net = rq.net_hours_for_period(date(2025,6,1), date(2025,6,14))
    df_net = pd.DataFrame(net)
    print("Columns returned:", list(df_net.columns))
    print(df_net)

    if not df_net.empty:
        # Use whatever the actual column name is (uppercase vs lowercase)
        idx_col = 'EMPLOYEE_ID' if 'EMPLOYEE_ID' in df_net.columns else 'employee_id'
        val_col = 'NET_HOURS'     if 'NET_HOURS'     in df_net.columns else 'net_hours'

        df_net.set_index(idx_col, inplace=True)
        df_net[val_col].nlargest(10).plot.barh()
        plt.title("Top 10 Net Hours (Jun 1–14)")
        plt.xlabel("Net Hours")
        plt.tight_layout()
        plt.show()
    else:
        print("No net‐hours data in that range.")

    # Example 2: Total meeting hours
    print(f"========================================")
    print(f"Example 2: Total meeting hours")
    meet = rq.total_meeting_hours()
    df_meet = pd.DataFrame(meet)
    print("\nMeeting hours per employee:")
    print(df_meet)

    # If you want to plot:
    if not df_meet.empty:
        idx = 'EMPLOYEE_ID' if 'EMPLOYEE_ID' in df_meet.columns else 'employee_id'
        val = 'TOTAL_MEETING_HOURS' if 'TOTAL_MEETING_HOURS' in df_meet.columns else 'total_meeting_hours'
        df_meet.set_index(idx, inplace=True)
        df_meet[val].nlargest(10).plot.barh(color='skyblue')
        plt.title("Top 10 Meeting Hours")
        plt.xlabel("Hours")
        plt.tight_layout()
        plt.show()

    # Example 3: Absence summary for SL
    print(f"========================================")
    print(f"Example 3: Absence summary for SL")
    absn = rq.total_absences('SL')
    df_absn = pd.DataFrame(absn)
    print("\nSick‐leave summary:")
    print(df_absn)

    # Example 4: Percentages per month    
    print(f"========================================")
    print(f"Example 4: Percentages per month")
    percs = rq.work_absence_percentages()
    df_percs = pd.DataFrame(percs)
    print("\nWork vs Absence %:")
    print(df_percs)

    # You could pivot it for a nicer view:
    # df_percs.pivot(index=['EMPLOYEE_ID','EMPLOYEE_NAME'], columns=['YEAR','MONTH'], values='PCT_WORKED')
