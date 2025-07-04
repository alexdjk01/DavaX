import oracledb

from tables_structure.dim_tables import DimTables
from tables_structure.fact_table import FactTable
from tables_structure.source_tables import SourceTables
from utils.insert_values_into_tables import InsertValuesIntoTables



if __name__ == "__main__":
    connection = oracledb.connect(
        user='mada',
        password='madalin2001',
        dsn='localhost:1521/XEPDB1'
    )

    dim_tables = DimTables(connection)
    source_tables = SourceTables(connection)

    dim_tables.create_tables()
    source_tables.create_tables()

    # Populate the dimension tables with data from source tables
    InsertValuesIntoTables.populate_dim_employees(connection.cursor())  
    InsertValuesIntoTables.populate_dim_projects(connection.cursor())
    InsertValuesIntoTables.populate_dim_events(connection.cursor())

    # Insert values into fact table
    fact_table = FactTable(connection.cursor())

    fact_table.populate_fact_timesheets()
