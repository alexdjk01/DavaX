import csv
import cx_Oracle
from datetime import datetime


DB_CONFIG = {
    "user": "alex",
    "password": "parola",
    "dsn": "localhost:1521/XEPDB1",
}

def get_connection():
    return oracledb.connect(**DB_CONFIG)

def get_employee_ids_for_event(cursor, event_id, source_table):
    cursor.execute(f"""
        SELECT e.employee_id
        FROM {source_table} s
        JOIN dim_employees e ON s.email = e.email
        WHERE s.event_id = :event_id
    """, {"event_id": event_id})
    return [row[0] for row in cursor.fetchall()]

def get_date_id(cursor, event_id):
    cursor.execute("""
        SELECT d.date_id
        FROM dim_dates d
        JOIN dim_events e ON TRUNC(e.event_date) = d.date_id
        WHERE e.event_id = :event_id
    """, {"event_id": event_id})
    row = cursor.fetchone()
    return row[0] if row else None

def get_project_id(cursor, name):
    cursor.execute("SELECT project_id FROM dim_projects WHERE project_name = :name", {"name": name})
    row = cursor.fetchone()
    return row[0] if row else None

def get_event_quantities(cursor, event_id, source_table):
    cursor.execute(f"""
        SELECT e.employee_id, s.quantity
        FROM {source_table} s
        JOIN dim_employees e ON s.email = e.email
        WHERE s.event_id = :event_id
    """, {"event_id": event_id})
    return cursor.fetchall()

def insert_fact(cursor, employee_id, event_id, date_id, project_id, quantity):
    cursor.execute("""
        MERGE INTO fact_timesheets f
        USING dual ON (
            f.employee_id = :emp AND f.event_id = :evt AND f.date_id = :dt AND f.project_id = :prj
        )
        WHEN NOT MATCHED THEN
        INSERT (employee_id, event_id, date_id, project_id, quantity)
        VALUES (:emp, :evt, :dt, :prj, :qty)
    """, {
        "emp": employee_id, "evt": event_id, "dt": date_id,
        "prj": project_id, "qty": quantity
    })

def process_events(cursor, source_table):
    cursor.execute("SELECT event_id FROM dim_events")
    all_event_ids = [row[0] for row in cursor.fetchall()]
    prj = get_project_id(cursor, 'DavaX')

    for event_id in all_event_ids:
        date_id = get_date_id(cursor, event_id)
        if source_table == "src_confluence_absences":
            source = "src_confluence_absences"
        elif source_table == "src_meetings":
            source = "src_meetings"
        else:
            continue

        for emp_id, qty in get_event_quantities(cursor, event_id, source):
            insert_fact(cursor, emp_id, event_id, date_id, prj, qty)

def main():
    conn = get_connection()
    cur = conn.cursor()

    process_events(cur, "src_confluence_absences")
    process_events(cur, "src_meetings")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()