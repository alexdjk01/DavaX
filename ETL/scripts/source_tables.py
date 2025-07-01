import oracledb

from utils.utils import Utils

connection = oracledb.connect(
    user='alex',
    password='parola',
    dsn='localhost:1521/XEPDB1'
)

# define the cursor
cursor = connection.cursor()

# create tables

tables = [
    {
        "name": "src_timesheet_pontaj",
        "columns": [
            ("pontaj_id", "NUMBER PRIMARY KEY"),
            ("first_name", "VARCHAR2(50)"),
            ("last_name", "VARCHAR2(50)"),
            ("email", "VARCHAR2(100)"),
            ("project_name", "VARCHAR(100)"),
            ("date", "DATE"),
            ("quantity", "NUMBER")
        ]
    },
    {
        "name": "src_timesheet_absences",
        "columns": [
            ("absence_id", "NUMBER PRIMARY KEY"),
            ("first_name", "VARCHAR2(50)"),
            ("last_name", "VARCHAR2(50)"),
            ("email", "VARCHAR2(100)"),
            ("absence_type", "VARCHAR(10)"),
            ("date", "DATE"),
            ("quantity", "NUMBER")
        ]
    },

]


# execute all table creation statements
for table in tables:
    cursor.execute(Utils.create_table(table_name=table.get('name'),
                                      columns=table.get('columns'),
                                      constraints=table.get('constraints')))

# commit the changes
connection.commit()
cursor.close()
connection.close()

# print statement to verify if correct
print("Tables created successfully.")