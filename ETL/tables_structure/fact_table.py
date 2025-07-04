class FactTable:
    """
    Class representing the structure of the fact table in the database.
    """
    def __init__(self, cursor):
        """
        Initializes the FactTable class with a database self.cursor."""
        self.cursor = cursor

    def get_project_id(self, project_name):
        """
        Returns the project_id for a given project_name from the dim_projects table.
        If the project does not exist, returns None."""
        self.cursor.execute(
            "SELECT project_id FROM dim_projects WHERE project_name = :name", 
            {"name": project_name}
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_date_id(self, event_date):
        """Returns the date_id for a given event_date from the dim_dates table.
        If the date does not exist, returns None."""
        self.cursor.execute(
            """
            SELECT date_id FROM dim_dates
             WHERE year = :year AND month = :month AND day = :day
            """,
            {"year": event_date.year, "month": event_date.month, "day": event_date.day}
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_event_quantities(self, event_name, event_type, event_date):
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
                   AND TRUNC(s.meeting_date) = :event_date
            """
            params = {"event_name": event_name, "event_date": event_date}
        # Full-day absences from CSV
        elif event_type in ("UL", "SL", "AL"):
            sql = """
                SELECT emp.employee_id, s.quantity
                  FROM src_timesheet_absences s
                  JOIN dim_employees emp ON s.email = emp.email
                 WHERE s.absence_type = :event_type
                   AND TRUNC(s.absence_date) = :event_date
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
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def insert_fact(self, emp_id, event_id, date_id, project_id, quantity):
        """
        Inserts a record into the fact_timesheets table.
        If the record already exists, it updates the quantity."""
        self.cursor.execute(
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
             "prj": project_id, "qty": quantity})

    def populate_fact_timesheets(self):
        project_id = self.get_project_id("DavaX")

        self.cursor.execute("SELECT event_id, event_name, event_type, event_date FROM dim_events")
        for event_id, event_name, event_type, event_date in self.cursor.fetchall():
            date_id = self.get_date_id(event_date)
            if date_id is None:
                continue
            for emp_id, qty in self.get_event_quantities(event_name,
                                                         event_type,
                                                         event_date):
                self.insert_fact(emp_id,
                                 event_id,
                                 date_id,
                                 project_id,
                                 qty)

        print("Inserted data records into fact_timesheets")