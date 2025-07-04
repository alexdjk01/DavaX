import oracledb
import pandas as pd
import os


def file_path(name):
    base_path = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_path, 'files', name)


def load_csvs():
    return {
        'pontaj': pd.read_csv(file_path('source_timesheet_pontaj.csv')),
        'absences': pd.read_csv(file_path('source_timesheet_absences.csv')),
        'meetings': pd.read_csv(file_path('src_meetings.csv')),
        'confluence': pd.read_csv(file_path('source_confluence_absences.csv')),
    }


def populate_dim_employees(cursor, pontaj_df, absences_df, meetings_df=None):
    employees_df = pd.concat([
        pontaj_df[['first_name', 'last_name', 'email']],
        absences_df[['first_name', 'last_name', 'email']],
        meetings_df[['first_name', 'last_name', 'email']]
    ]).drop_duplicates().dropna()

    cursor.executemany("""
        INSERT INTO dim_employees (first_name, last_name, email)
        VALUES (:1, :2, :3)
    """, employees_df.values.tolist())
    print("dim_employees populat")


def populate_dim_projects(cursor, pontaj_df):
    projects_df = pontaj_df[['project_name']].drop_duplicates().dropna()

    cursor.executemany("""
        INSERT INTO dim_projects (project_name)
        VALUES (:1)
    """, projects_df.values.tolist())
    print("dim_projects populat")


def populate_dim_events(cursor, absences_df, meetings_df, confluence_df):
    # src_timesheet_absences
    events_1 = absences_df[['absence_date', 'absence_type']].drop_duplicates().dropna()
    events_1['event_name'] = 'absence'
    events_1.columns = ['event_date', 'event_name', 'event_type']

    # src_meetings
    events_2 = meetings_df[['meeting_date', 'meeting_title']].drop_duplicates().dropna()
    events_2['event_type'] = 'meeting'
    events_2.columns = ['event_date', 'event_name', 'event_type']

    # src_confluence_absences
    events_3 = confluence_df[['start_date', 'subject']].drop_duplicates().dropna()
    events_3['event_name'] = 'absence'
    events_3.columns = ['event_date', 'event_name', 'event_type']

    # Combination of all events
    all_events = pd.concat([events_1, events_2, events_3])[['event_date', 'event_name', 'event_type']]
    all_events = all_events.drop_duplicates()
    all_events['event_date'] = pd.to_datetime(all_events['event_date'], errors='coerce')

    cursor.executemany("""
        INSERT INTO dim_events (event_date, event_name, event_type)
        VALUES (:1, :2, :3)
    """, [tuple(row) for row in all_events.itertuples(index=False)])
    print("dim_events populat")


def main():
    connection = oracledb.connect(
        user='mada',
        password='madalin2001',
        dsn='localhost:1521/XEPDB1'
    )
    cursor = connection.cursor()

    data = load_csvs()

    populate_dim_employees(cursor, data['pontaj'], data['absences'], data['meetings'])
    populate_dim_projects(cursor, data['pontaj'])
    populate_dim_events(cursor, data['absences'], data['meetings'], data['confluence'])

    connection.commit()
    print("Toate tabelele de dimensiuni au fost populate cu succes.")
    
    cursor.close()
    connection.close()


if __name__ == '__main__':
    main()
