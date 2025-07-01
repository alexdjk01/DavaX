import pandas as pd
import oracledb

connection = oracledb.connect(
    user='alex',
    password='parola',
    dsn='localhost:1521/XEPDB1'
)

# define the cursor
cursor = connection.cursor()

# --- Step 1: Load CSVs
#timesheet_pontaj csv
pontaj_df = pd.read_csv("../files/src_timesheet_pontaj.csv")
pontaj_df["date"] = pd.to_datetime(pontaj_df["date"]).dt.date
pontaj_df = pontaj_df.where(pd.notnull(pontaj_df), None)
pontaj_data = list(pontaj_df.itertuples(index=False, name=None))

#timesheet_absences csv
absences_df = pd.read_csv("../files/src_timesheet_absences.csv")
absences_df["date"] = pd.to_datetime(absences_df["date"]).dt.date
absences_df = absences_df.where(pd.notnull(absences_df), None)
absences_data = list(absences_df.itertuples(index=False, name=None))

# --- Step 2: Insert data
insert_pontaj = """
INSERT INTO src_timesheet_pontaj (
    pontaj_id, first_name, last_name, email, project_name, date, quantity
) VALUES (
    :1, :2, :3, :4, :5, :6, :7
)
"""
cursor.execute("TRUNCATE TABLE src_timesheet_pontaj")
cursor.executemany(insert_pontaj, pontaj_data)
print(f"Inserted {cursor.rowcount} records into src_timesheet_pontaj")

insert_absences = """
INSERT INTO src_timesheet_absences (
    absence_id, first_name, last_name, email, absence_type, date, quantity
) VALUES (
    :1, :2, :3, :4, :5, :6, :7
)
"""
cursor.execute("TRUNCATE TABLE src_timesheet_absences")
cursor.executemany(insert_absences, absences_data)
print(f"Inserted {cursor.rowcount} records into src_timesheet_absences")

# --- Step 3: Commit changes
connection.commit()
cursor.close()
connection.close()

# print statement to verify if correct
print("Insert finished successfully.")

# TODO : Insert data from MODELED CSV: meeting (teams) and absence(calendar confluence)