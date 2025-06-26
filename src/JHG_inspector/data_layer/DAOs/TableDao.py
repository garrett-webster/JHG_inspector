from abc import ABC, abstractmethod
from sqlite3 import Connection

def set_sql_strings(cls):
    table_name = cls.__name__
    cls.table_name = table_name[:-3]


    return cls

class TableDoa(ABC):
    def __init__(self, connection: Connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.column_names_string = ""
        self.placeholder_string = ""

        # self.column_names = ", ".join([column[0] for column in columns])
        # self.placeholders = ", ".join(["?" for _ in columns])

    def set_strings(self):
        ...

    @abstractmethod
    def insert(self, values):
        ...

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