import pandas as pd


class Utils:
    """
    A collection of static utility functions for data processing, validation,
    formatting, and miscellaneous helper tasks used throughout the application.

    This class is designed to provide general-purpose, reusable functions
    that can be accessed without instantiating the class.

    """

    @staticmethod
    def drop_table(table_name):
        """
            Generates a SQL statement to drop a table along with all its constraints.

            This function returns a SQL command string that drops the specified table
            and cascades the deletion to all dependent foreign key constraints.

            param:
                table_name (str): The name of the table to be dropped.

            return:
                str: A SQL statement to drop the table with CASCADE CONSTRAINTS.
        """
        return f"DROP TABLE {table_name} CASCADE CONSTRAINTS"

    @staticmethod
    def create_table(table_name, columns, constraints=None):
        """
            Generates a SQL statement to create a table with columns and optional constraints.

            params:
                table_name (str): The name of the table to create.
                columns (list[tuple]): A list of (column_name, column_type) tuples.
                constraints (list[str], optional): Additional table-level constraint strings.

            return:
                str: A full CREATE TABLE SQL statement.

            example:
                Utils.create_table_sql(
                    "users",
                    [("id", "NUMBER PRIMARY KEY"), ("name", "VARCHAR2(50)")],
                    ["UNIQUE (name)"]
                )
        """
        column_definitions = [f"{col} {dtype}" for col, dtype in columns]

        if constraints:
            column_definitions += constraints
        columns_sql = ",\n    ".join(column_definitions)

        return f"CREATE TABLE {table_name} (\n    {columns_sql}\n)"

    @staticmethod
    def insert_values_into_tables(table_name, columns):
        """
        Generates a parameterized SQL INSERT statement for use with Oracle databases.

        This method builds an INSERT INTO statement using bind variables (e.g., :1, :2, ...)
        which is compatible with Oracle's `cursor.executemany()` method. It ensures safe 
        and efficient insertion of multiple rows into the specified table.

        params:
            table_name (str): The name of the table to insert data into.
            columns (list[str]): A list of column names in the table to populate.

        return:
            str: A SQL INSERT statement with bind variables.

        """
        col_sql = ", ".join(columns)
        bind_sql = ", ".join([f":{i+1}" for i in range(len(columns))])

        return f"INSERT INTO {table_name} ({col_sql}) VALUES ({bind_sql})"

    @staticmethod
    def get_column_names(cursor, table_name):
        """
        Returns the column names for a given Oracle table.

        params:
            cursor (oracledb.Cursor): The Oracle DB cursor.
            table_name (str): The name of the table (case-insensitive).

        return:
            list[str]: List of column names in the table.
        """
        column_names = """
            SELECT column_name
                FROM user_tab_columns
                    WHERE table_name = :1
            ORDER BY column_id
        """
        cursor.execute(column_names, [table_name.upper()])

        # fetch all column names and return them as a list
        return [row[0] for row in cursor.fetchall()]

    def process_csv(file_path, date):
        """
        Reads a CSV file into a pandas DataFrame, processes it by dropping NaN values,
        and returns the DataFrame.

        params:
            file_path (str): The path to the CSV file.
            date (str): The date column from CSV file

        return:
            pd.DataFrame: Processed DataFrame with NaN values dropped.
        """
        data_frame = pd.read_csv(file_path)
        data_frame[date] = pd.to_datetime(data_frame[date]).dt.date
        data_frame = data_frame.where(pd.notnull(data_frame), None)
        data_frame = list(data_frame.itertuples(index=False, name=None))

        return data_frame
