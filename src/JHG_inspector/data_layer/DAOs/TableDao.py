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
        self.cursor = connection.cursor()

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

    def insert(self, values):
        cls = self.__class__
        self.cursor.executemany(
            f"INSERT INTO {cls.table_name} ({cls.column_names_string}) VALUES ({cls.placeholder_string})",
            values
        )

    @abstractmethod
    def select_one(self):
        ...

    @abstractmethod
    def select_all(self):
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