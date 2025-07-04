import oracledb
from datetime import datetime


DB_CONFIG = {
    "user": "dariusdinu",
    "password": "parolamea",
    "dsn": "localhost:1521/XEPDB1",
}

def get_connection():
    return oracledb.connect(**DB_CONFIG)

def get_project_id(cursor, project_name):
    cursor.execute(
        "SELECT project_id FROM dim_projects WHERE project_name = :name", 
        {"name": project_name}
    )
    row = cursor.fetchone()
    return row[0] if row else None

def get_date_id(cursor, event_date):
    cursor.execute(
        """
        SELECT date_id FROM dim_dates
         WHERE year = :year AND month = :month AND day = :day
        """,
        {"year": event_date.year, "month": event_date.month, "day": event_date.day}
    )
    row = cursor.fetchone()
    return row[0] if row else None

def get_event_quantities(cursor, event_name, event_type, event_date):
    """
    Returns list of (employee_id, quantity) for this event,
    selecting from the appropriate source and filtering by date.
    """
    # Meeting attendance
    if event_type.lower() == "meeting":
        sql = """
            SELECT emp.employee_id, s.quantity
              FROM src_meetings s
              JOIN dim_employees emp ON s.email = emp.email
             WHERE s.meeting_title = :event_name
               AND TRUNC(s.current_date) = :event_date
        """
        params = {"event_name": event_name, "event_date": event_date}
    # Full-day absences from CSV
    elif event_type in ("UL", "SL", "AL"):  
        sql = """
            SELECT emp.employee_id, s.quantity
              FROM src_timesheet_absences s
              JOIN dim_employees emp ON s.email = emp.email
             WHERE s.absence_type = :event_type
               AND TRUNC(s.current_date) = :event_date
        """
        params = {"event_type": event_type, "event_date": event_date}
    # Partial absences from Confluence
    else:
        sql = """
            SELECT emp.employee_id, s.quantity
              FROM src_confluence_absences s
              JOIN dim_employees emp
                ON s.first_name = emp.first_name
               AND s.last_name  = emp.last_name
             WHERE s.absence_type = :event_type
               AND TRUNC(s.start_time) = :event_date
        """
        params = {"event_type": event_type, "event_date": event_date}
    cursor.execute(sql, params)
    return cursor.fetchall()

def insert_fact(cursor, emp_id, event_id, date_id, project_id, quantity):
    cursor.execute(
        """
        MERGE INTO fact_timesheets f
        USING dual
          ON (f.employee_id = :emp AND f.event_id = :evt 
               AND f.date_id = :dt AND f.project_id = :prj)
        WHEN NOT MATCHED THEN
          INSERT (employee_id, event_id, date_id, project_id, quantity)
          VALUES (:emp, :evt, :dt, :prj, :qty)
        """,
        {"emp": emp_id, "evt": event_id, "dt": date_id,
         "prj": project_id, "qty": quantity}
    )

def main():
    conn = get_connection()
    cur = conn.cursor()

    project_id = get_project_id(cur, "DavaX")

    cur.execute("SELECT event_id, event_name, event_type, event_date FROM dim_events")
    for event_id, event_name, event_type, event_date in cur.fetchall():
        date_id = get_date_id(cur, event_date)
        if date_id is None:
            continue
        for emp_id, qty in get_event_quantities(cur, event_name, event_type, event_date):
            insert_fact(cur, emp_id, event_id, date_id, project_id, qty)

    print(f"Inserted data records into fact_timesheets")
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()