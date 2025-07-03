import oracledb

from tables_structure.dim_tables import DimTables
from tables_structure.source_tables import SourceTables
from utils.insert_values_into_tables import InsertValuesIntoTables



if __name__ == "__main__":
    connection = oracledb.connect(
        user='dan',
        password='davax_pass',
        dsn='localhost:1521/XEPDB1'
    )

    dim_tables = DimTables(connection)
    source_tables = SourceTables(connection)

    dim_tables.create_tables()
    source_tables.create_tables()
