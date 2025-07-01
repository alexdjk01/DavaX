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
