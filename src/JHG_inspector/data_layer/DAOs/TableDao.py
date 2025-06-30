import json
from abc import ABC, abstractmethod
from pathlib import Path
from sqlite3 import Connection

from src.JHG_inspector.data_layer.DB_init import TableData

class TableDoa(ABC):
    with open(Path(__file__).parent.parent / "schema.json", "r") as f:
        schema = json.load(f)

    def __init__(self, connection: Connection):
        self.connection = connection
        self.cls = self.__class__

        # Automatically prepare SQL strings (only once per subclass)
        cls = self.__class__
        if not getattr(cls, "_sql_strings_initialized", False):
            cls.prepare_sql_strings()
            cls._sql_strings_initialized = True

    @classmethod
    def prepare_sql_strings(cls):
        """Prepares the column name and placeholder strings to be used in insert statements

           Gets the schema of the table with name table_name and creates a string (column_names_string) that can be
           used in creating a SQL insert statement. Also creates a string of question marks with the same number of
           question marks as column names.
           """

        class_name = cls.__name__
        cls.table_name = class_name[0].lower() + class_name[1:-3]

        if cls.table_name not in TableDoa.schema:
            raise ValueError(f"No schema found for table '{cls.table_name}' in schema.json")

        table_data = TableData(TableDoa.schema[cls.table_name])
        columns = table_data.non_excluded_columns

        if ('gameId', 'INTEGER') in table_data.columns:
            cls.column_names_string = ", ".join(["gameId"] + [col[0] for col in columns])
            cls.placeholder_string = ", ".join(["?"] * (len(columns) + 1))
        else:
            cls.column_names_string = ", ".join([col[0] for col in columns])
            cls.placeholder_string = ", ".join(["?"] * len(columns))

    def insert(self, values: list[tuple]):
        """Performs an insert operation into the database, using the values passed in values.

        Parameters
        ----------
        values : list[tuple]
            values is a list of tuples where each tuple is the data for one record to be inserted.
            """

        self.connection.executemany(
            f"INSERT INTO {self.cls.table_name} ({self.cls.column_names_string}) VALUES ({self.cls.placeholder_string})",
            values
        )

    def select(self, select_columns: list[str], matching_columns: list[str], matching_vals: list):
        """Performs a select operation on the database.

           Parameters
           ----------
           select_columns: list[str]
               A list of the columns to be returned, as strings
           matching_columns: list[str]
               A list of columns that you want to match against, as strings. Each string is turned into a string like
               'column = ?' where column is a string in matching_columns
           matching_vals: list
               The values that the columns in matching_columns should be compared against. Must be in the same order as
               their corresponding column in matching_columns.
               """

        select_columns_string = ", ".join(select_columns)

        cursor = self.connection.cursor()
        if matching_columns:
            matching_columns_string = " AND ".join([column + " = ?" for column in matching_columns])
            return cursor.execute(f"SELECT {select_columns_string} FROM {self.cls.table_name} WHERE {matching_columns_string}",
                       matching_vals)
        else:
            return cursor.execute(
                f"SELECT {select_columns_string} FROM {self.cls.table_name}", matching_vals)

    def select_one(self, select_columns, matching_columns, matching_vals):
        return self.select(select_columns, matching_columns, matching_vals).fetchone()

    def select_all(self, select_columns: list[str], matching_columns: list[str], matching_vals: list):
        return self.select(select_columns, matching_columns, matching_vals).fetchall()

    def select_all(self, select_columns: list[str]):
        return self.select(select_columns, [], []).fetchall()

    @abstractmethod
    def select_id(self, matching_columns, matching_vals):
        ...

    def __init_subclass__(cls, **kwargs):
        """Ensures that all subclasses follow the TablenameDao naming convention (which the prepare_sql_strings method
        relies on).

        If the name does not end in 'Dao' or the prefix is not a table found in the schema, then an error is raised.
        """

        super().__init_subclass__(**kwargs)

        # Enforce naming convention
        if not cls.__name__.endswith("Dao"):
            raise TypeError(f"Class name '{cls.__name__}' must end with 'Dao'")

        table_name = cls.__name__[0].lower() + cls.__name__[1:-3]
        if table_name not in TableDoa.schema:
            raise ValueError(f"Table name '{table_name}' not found in schema for class '{cls.__name__}'")