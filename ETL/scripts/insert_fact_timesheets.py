import csv
import cx_Oracle
from datetime import datetime


DB_CONFIG = {
    "user": "alex",
    "password": "parola",
    "dsn": "localhost:1521/XEPDB1",
}

def get_connection():
    return cx_Oracle.connect(**DB_CONFIG)

def get_employee_id(cursor, email):
    cursor.execute("SELECT employee_id FROM dim_employees WHERE email = :email", {"email": email})
    row = cursor.fetchone()
    return row[0] if row else None

def get_date_id(cursor, event_id):
    cursor.execute("""
        SELECT d.date_id
        FROM dim_dates d
        JOIN dim_events e ON TRUNC(e.event_date) = d.date_id
        WHERE e.event_id = :event_id
    """, {"event_id": event_id})
    row = cursor.fetchone()
    return row[0] if row else None

def get_or_create_event_id(cursor, name, type_, organizer):
    cursor.execute("""
        SELECT event_id FROM dim_events
        WHERE event_name = :name AND event_type = :type AND event_organizer = :org
    """, {"name": name, "type": type_, "org": organizer})
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("""
        INSERT INTO dim_events (event_name, event_type, event_organizer)
        VALUES (:name, :type, :org) RETURNING event_id INTO :id
    """, {"name": name, "type": type_, "org": organizer, "id": cursor.var(cx_Oracle.NUMBER)})
    return cursor.getimplicitresults()[0][0]

def get_project_id(cursor, name):
    cursor.execute("SELECT project_id FROM dim_projects WHERE project_name = :name", {"name": name})
    row = cursor.fetchone()
    return row[0] if row else None

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

def process_csv(file_path, record_fn):
    with open(file_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record_fn(row)

def main():
    conn = get_connection()
    cur = conn.cursor()

    def handle_absence(row):
        emp = get_employee_id(cur, row['email'])
        evt = get_or_create_event_id(cur, row['absence_type'], row['absence_type'], 'HR System')
        dt = get_date_id(cur, evt)
        prj = get_project_id(cur, 'DavaX')
        insert_fact(cur, emp, evt, dt, prj, float(row['quantity']))

    def handle_pontaj(row):
        emp = get_employee_id(cur, row['email'])
        evt = get_or_create_event_id(cur, 'Work', 'Standard Time', 'Self')
        dt = get_date_id(cur, evt)
        prj = get_project_id(cur, row['project_name'])
        insert_fact(cur, emp, evt, dt, prj, float(row['quantity']))

    def handle_meeting(row):
        emp = get_employee_id(cur, row['email'])
        evt = get_or_create_event_id(cur, row['meeting_title'], 'Meeting', 'Academy')
        dt = get_date_id(cur, evt)
        prj = get_project_id(cur, 'DavaX')
        insert_fact(cur, emp, evt, dt, prj, float(row['quantity']))

    process_csv("data/src_timesheet_absences.csv", handle_absence)
    process_csv("data/src_timesheet_pontaj.csv", handle_pontaj)
    process_csv("data/src_meetings.csv", handle_meeting)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()

