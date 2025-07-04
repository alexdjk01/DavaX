import os
import pandas as pd

from datetime import datetime, timedelta

from utils.utils import Utils


class InsertValuesIntoTables:
    """
    Class to handle the insertion of values into database tables.
    """
    @staticmethod
    def populate_dim_date_table():
        """
            Generates a SQL statement to populate a date dimension table with dates.

            return:
                str: a list of tuples containing date values for the current year.
        """
        # get the current year
        current_year = datetime.now().year

        # get the start and end dates for the current year
        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 12, 31)

        current_date = start_date

        # create a list to hold the values for the date dimension table
        data_values = list()

        # get the values for the date dimension table
        while current_date <= end_date:
            date_id = current_date.date()
            year = current_date.year
            month = current_date.month
            day = current_date.day
            quarter = (month - 1) // 3 + 1

            data_values.append((date_id, year, month, quarter, day))

            # increment the current date by one day
            current_date += timedelta(days=1)

        return data_values
    
    @staticmethod
    def populate_dim_employees(cursor):
        query = """
            INSERT INTO dim_employees (first_name, last_name, email)
            SELECT DISTINCT first_name, last_name, email FROM (
                SELECT first_name, last_name, email FROM src_timesheet_pontaj
                UNION
                SELECT first_name, last_name, email FROM src_timesheet_absences
                UNION
                SELECT first_name, last_name, email FROM src_meetings
            )
            WHERE email NOT IN (SELECT email FROM dim_employees)
        """
        cursor.execute(query)
        cursor.connection.commit()


    @staticmethod
    def populate_dim_projects(cursor):
        query = """
            INSERT INTO dim_projects (project_name)
            SELECT DISTINCT project_name FROM src_timesheet_pontaj
            WHERE project_name IS NOT NULL
              AND project_name NOT IN (SELECT project_name FROM dim_projects)
        """
        cursor.execute(query)
        cursor.connection.commit()

    @staticmethod
    def populate_dim_events(cursor):
        queries = [
            # meetings → current_date + meeting_title + 'meeting'
            """
            INSERT INTO dim_events (event_date, event_name, event_type)
            SELECT DISTINCT current_date, meeting_title, 'meeting'
            FROM src_meetings
            WHERE (current_date, meeting_title, 'meeting') NOT IN (
                SELECT event_date, event_name, event_type FROM dim_events
            )
            """,

            # timesheet absences → current_date + 'absence' + absence_type
            """
            INSERT INTO dim_events (event_date, event_name, event_type)
            SELECT DISTINCT current_date, 'absence', absence_type
            FROM src_timesheet_absences
            WHERE (current_date, 'absence', absence_type) NOT IN (
                SELECT event_date, event_name, event_type FROM dim_events
            )
            """,

            # confluence absences → TRUNC(start_time) + 'absence' + absence_type
            """
            INSERT INTO dim_events (event_date, event_name, event_type)
            SELECT DISTINCT TRUNC(start_time), 'absence', absence_type
            FROM src_confluence_absences
            WHERE (TRUNC(start_time), 'absence', absence_type) NOT IN (
                SELECT event_date, event_name, event_type FROM dim_events
            )
            """
        ]

        for query in queries:
            cursor.execute(query)
            
        cursor.connection.commit()



    @staticmethod
    def insert_values_into_source_tables(cursor):
        """
        Inserts values into a specified source table using a cursor.

        :param cursor: An Oracle database cursor to execute SQL commands.
        :param table_name: The name of the table to insert data into.
        """
        pontaj_path = os.path.join(os.getcwd(), "files", "source_timesheet_pontaj.csv")
        timesheet_absences_path = os.path.join(os.getcwd(), "files", "source_timesheet_absences.csv")
        confluence_absences_path = os.path.join(os.getcwd(), "files", "source_confluence_absences.csv")
        meetings_path = os.path.join(os.getcwd(), "files", "src_meetings.csv")

        meetings_df = pd.read_csv(meetings_path)

        pontaj_data = Utils.process_csv(pontaj_path, "pontaj_date")
        absences_data = Utils.process_csv(timesheet_absences_path, "absence_date")

        # rotunjește coloana quantity
        meetings_df["quantity"] = meetings_df["quantity"].astype(float).round(2)
        meetings_df["meeting_date"] = pd.to_datetime(meetings_df["current_date"], errors="coerce").dt.date
        # pregătește datele pentru inserare (exclude meeting_id, se generează în DB)
        meetings_data = list(meetings_df[[
            "meeting_id","meeting_title", "current_date", "first_name", "last_name", "email", "quantity"
        ]].itertuples(index=False, name=None))

        confluence_absences_df = pd.read_csv(confluence_absences_path)

        # merge start_date start_time into one timestamp. Same for end time and date
        confluence_absences_df["start_timestamp"] = pd.to_datetime(
            confluence_absences_df["start_date"] + " " + confluence_absences_df["start_time"],
            format="%Y-%m-%d %I:%M:%S %p"  # 12-hour format with AM/PM
        )
        confluence_absences_df["end_timestamp"] = pd.to_datetime(
            confluence_absences_df["end_date"] + " " + confluence_absences_df["end_time"],
            format="%Y-%m-%d %I:%M:%S %p"
        )

        # add a calculated column quantity that calculates the difference between start and end time timestamp
        confluence_absences_df["quantity"] = \
            round((confluence_absences_df["end_timestamp"] - confluence_absences_df["start_timestamp"]).dt.total_seconds() / 3600, 2)

        # --- Step 2: Insert data
        insert_pontaj = """
        INSERT INTO src_timesheet_pontaj (
            first_name, last_name, email, project_name, current_date, quantity
        ) VALUES (
            :1, :2, :3, :4, :5, :6
        )
        """
        cursor.execute("TRUNCATE TABLE src_timesheet_pontaj")
        cursor.executemany(insert_pontaj, pontaj_data)
        print(f"Inserted {cursor.rowcount} records into src_timesheet_pontaj")
        # ===========================================================
        insert_absences = """
        INSERT INTO src_timesheet_absences (
            first_name, last_name, email, absence_type, current_date, quantity
        ) VALUES (
            :1, :2, :3, :4, :5, :6
        )
        """
        cursor.execute("TRUNCATE TABLE src_timesheet_absences")
        cursor.executemany(insert_absences, absences_data)
        print(f"Inserted {cursor.rowcount} records into src_timesheet_absences")
        # ===========================================================
        insert_meetings = """
        INSERT INTO src_meetings (
            meeting_id, meeting_title, current_date, first_name, last_name, email, quantity
        ) VALUES (
            :1, :2, :3, :4, :5, :6,:7
        )
        """
        cursor.execute("TRUNCATE TABLE src_meetings")
        cursor.executemany(insert_meetings, meetings_data)
        print(f"Inserted {cursor.rowcount} records into src_timesheet_absences")
        # ===========================================================
        insert_confluence_absences = """
        INSERT INTO src_confluence_absences (
            last_name, first_name, absence_type, start_time, end_time, all_day_event, quantity
        ) VALUES (
            :1, :2, :3, :4, :5, :6, :7
        )
        """
        # -- rename subject to absence_type as in the database table
        if "subject" in confluence_absences_df.columns:
            confluence_absences_df = confluence_absences_df.rename(columns={"subject": "absence_type"})
        # -- ensure proper values to bo inserted into oracle db
        confluence_absences_df["quantity"] = confluence_absences_df["quantity"].astype(int)
        print(confluence_absences_df)
        data_to_insert = list(confluence_absences_df[["last_name", "first_name", "absence_type","start_timestamp", "end_timestamp", "all_day_event", "quantity"]].itertuples(index=False, name=None))
        cursor.execute("TRUNCATE TABLE src_confluence_absences")
        cursor.executemany(insert_confluence_absences, data_to_insert)
        print(f"Inserted {cursor.rowcount} records into src_confluence_absences")

        print("Insert finished successfully.")