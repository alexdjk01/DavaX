import oracledb
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt

from tables_structure.dim_tables import DimTables
from tables_structure.source_tables import SourceTables
from tables_structure.fact_table import FactTable
from utils.insert_values_into_tables import InsertValuesIntoTables
from utils.queries import ReportQueries

if __name__ == "__main__":
    # 1) Open connectionection & build schema
    connection = oracledb.connect(
        user='dan',
        password='davax_pass',
        dsn='localhost:1521/XEPDB1'
    )

    dim_tables = DimTables(connection)
    source_tables = SourceTables(connection)

    dim_tables.create_tables()
    source_tables.create_tables()

    InsertValuesIntoTables.populate_dim_employees(connection.cursor())
    InsertValuesIntoTables.populate_dim_projects(connection.cursor())
    InsertValuesIntoTables.populate_dim_events(connection.cursor())

    fact_table = FactTable(connection.cursor())
    fact_table.populate_fact_timesheets()
    # ─────────── Run Reports ───────────
    report_queries = ReportQueries(connection)

    # Example 1: Net hours for June 1–14
    print("========================================")
    print("Example 1: Net hours for June 1–14")
    net = report_queries.net_hours_for_period(date(2025, 6, 1), date(2025, 6, 14))
    df_net = pd.DataFrame(net)
    print("Columns returned:", list(df_net.columns))
    print(df_net)

    if not df_net.empty:
        # Use whatever the actual column name is (uppercase vs lowercase)
        idx_col = 'EMPLOYEE_ID' if 'EMPLOYEE_ID' in df_net.columns else 'employee_id'
        val_col = 'NET_HOURS' if 'NET_HOURS' in df_net.columns else 'net_hours'

        df_net.set_index(idx_col, inplace=True)
        df_net[val_col].nlargest(10).plot.barh()
        plt.title("Top 10 Net Hours (Jun 1–14)")
        plt.xlabel("Net Hours")
        plt.tight_layout()
        plt.show()
    else:
        print("No net‐hours data in that range.")

    # Example 2: Total meeting hours
    print("========================================")
    print("Example 2: Total meeting hours")
    meet = report_queries.total_meeting_hours()
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
    print("========================================")
    print("Example 3: Absence summary for SL")
    absn = report_queries.total_absences('SL')
    df_absn = pd.DataFrame(absn)
    print("\nSick‐leave summary:")
    print(df_absn)

    # Example 4: Percentages per month    
    print("========================================")
    print("Example 4: Percentages per month")
    percs = report_queries.work_absence_percentages()
    df_percs = pd.DataFrame(percs)
    print("\nWork vs Absence %:")
    print(df_percs)

    # You could pivot it for a nicer view:
    # df_percs.pivot(index=['EMPLOYEE_ID','EMPLOYEE_NAME'], columns=['YEAR','MONTH'], values='PCT_WORKED')
