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