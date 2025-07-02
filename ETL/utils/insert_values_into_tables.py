from datetime import datetime, timedelta

from utils.utils import Utils


class InsertValuesIntoTables:
    """
    Class to handle the insertion of values into database tables.
    """

    @staticmethod
    def populate_date_table():
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
