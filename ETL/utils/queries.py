import oracledb
from datetime import date

class ReportQueries:
    """
    Encapsulates SQL report queries for the ETL star schema.
    Initialized with an existing Oracle DB connection.
    """
    def __init__(self, connection: oracledb.Connection):
        self.connection = connection

    def net_hours_for_period(self, start_date: date, end_date: date):
        """
        Total net hours (meetings positive, absences negative) per employee
        between start_date and end_date (inclusive).
        """
        sql = """
        SELECT
          e.employee_id,
          e.first_name || ' ' || e.last_name AS employee_name,
          ROUND(
            SUM(
              CASE WHEN ev.event_type = 'meeting' THEN f.quantity ELSE -f.quantity END
            ), 2
          ) AS net_hours
        FROM fact_timesheets f
        JOIN dim_employees e ON f.employee_id = e.employee_id
        JOIN dim_events    ev ON f.event_id      = ev.event_id
        WHERE ev.event_date BETWEEN :start_date AND :end_date
        GROUP BY e.employee_id, e.first_name, e.last_name
        ORDER BY net_hours DESC
        """
        binds = {"start_date": start_date, "end_date": end_date}
        cur = self.connection.cursor()
        cur.execute(sql, binds)
        cols = [c[0] for c in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return rows

    def daily_balance(self, start_date: date, end_date: date):
        """
        For each employee & year/month in the window, show pontaj_hours,
        absence_hours, and net_hours (pontaj - absence).
        """
        sql = """
        WITH
          pont AS (
            SELECT
              e.employee_id,
              d.date_id,
              d.year,
              d.month,
              SUM(s.quantity) AS pontaj_hours
            FROM src_timesheet_pontaj s
            JOIN dim_employees e ON s.email = e.email
            JOIN dim_dates    d ON TRUNC(s.pontaj_date) = d.date_id
            WHERE d.date_id BETWEEN :start_date AND :end_date
            GROUP BY e.employee_id, d.date_id, d.year, d.month
          ),
          absn AS (
            SELECT
              f.employee_id,
              d.date_id,
              d.year,
              d.month,
              SUM(f.quantity) AS absence_hours
            FROM fact_timesheets f
            JOIN dim_events  ev ON f.event_id = ev.event_id
            JOIN dim_dates   d  ON f.date_id  = d.date_id
            WHERE ev.event_type <> 'meeting'
              AND d.date_id BETWEEN :start_date AND :end_date
            GROUP BY f.employee_id, d.date_id, d.year, d.month
          )
        SELECT
          e.employee_id,
          e.first_name || ' ' || e.last_name AS employee_name,
          p.year,
          p.month,
          p.pontaj_hours,
          NVL(a.absence_hours,0)                 AS absence_hours,
          p.pontaj_hours - NVL(a.absence_hours,0) AS net_hours
        FROM dim_employees e
        JOIN pont p  ON e.employee_id = p.employee_id
        LEFT JOIN absn a ON e.employee_id = a.employee_id
                         AND p.date_id      = a.date_id
        ORDER BY p.year, p.month, p.pontaj_hours DESC
        """
        binds = {"start_date": start_date, "end_date": end_date}
        cur = self.connection.cursor()
        cur.execute(sql, binds)
        cols = [c[0] for c in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return rows

    def total_meeting_hours(self):
        """
        Total hours spent in meetings per employee.
        """
        sql = """
        SELECT
          e.employee_id,
          e.first_name || ' ' || e.last_name AS employee_name,
          ROUND(SUM(f.quantity), 2) AS total_meeting_hours
        FROM fact_timesheets f
        JOIN dim_events    ev ON f.event_id    = ev.event_id
        JOIN dim_employees e  ON f.employee_id = e.employee_id
        WHERE ev.event_type = 'meeting'
        GROUP BY e.employee_id, e.first_name, e.last_name
        ORDER BY total_meeting_hours DESC
        """
        cur = self.connection.cursor()
        cur.execute(sql)
        cols = [c[0] for c in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return rows

    def total_absences(self, absence_type: str):
        """
        Number of absence events and total absence hours for a given absence_type.
        """
        sql = """
        SELECT
          ev.event_type                  AS absence_type,
          COUNT(*)                       AS total_absence_events,
          ROUND(SUM(f.quantity), 2)      AS total_absence_hours
        FROM fact_timesheets f
        JOIN dim_events ev ON f.event_id = ev.event_id
        WHERE ev.event_type = :absence_type
        GROUP BY ev.event_type
        """
        binds = {"absence_type": absence_type}
        cur = self.connection.cursor()
        cur.execute(sql, binds)
        cols = [c[0] for c in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return rows

    def work_absence_percentages(self):
        """
        Percent of work (pontaj) vs. absence hours per employee per month.
        """
        sql = """
        WITH
          pontaj AS (
            SELECT e.employee_id, d.year, d.month, SUM(s.quantity) AS pontaj_hours
            FROM src_timesheet_pontaj s
            JOIN dim_employees e ON s.email = e.email
            JOIN dim_dates d       ON TRUNC(s.pontaj_date) = d.date_id
            GROUP BY e.employee_id, d.year, d.month
          ),
          absn AS (
            SELECT f.employee_id, d.year, d.month, SUM(f.quantity) AS absence_hours
            FROM fact_timesheets f
            JOIN dim_events ev  ON f.event_id = ev.event_id
            JOIN dim_dates  d   ON f.date_id  = d.date_id
            WHERE ev.event_type <> 'meeting'
            GROUP BY f.employee_id, d.year, d.month
          )
        SELECT
          e.employee_id,
          e.first_name || ' ' || e.last_name      AS employee_name,
          p.year,
          p.month,
          p.pontaj_hours,
          NVL(a.absence_hours, 0)                 AS absence_hours,
          ROUND(p.pontaj_hours
              / (p.pontaj_hours + NVL(a.absence_hours,0)) * 100, 2) AS pct_worked,
          ROUND(NVL(a.absence_hours,0)
              / (p.pontaj_hours + NVL(a.absence_hours,0)) * 100, 2) AS pct_absence
        FROM dim_employees e
        JOIN pontaj p ON e.employee_id = p.employee_id
        LEFT JOIN absn a ON e.employee_id = a.employee_id
                       AND p.year       = a.year
                       AND p.month      = a.month
        WHERE p.pontaj_hours > 0
        ORDER BY e.employee_id, p.year, p.month
        """
        cur = self.connection.cursor()
        cur.execute(sql)
        cols = [c[0] for c in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return rows
