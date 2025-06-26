from abc import ABC, abstractmethod
from sqlite3 import Connection


class TableDoa(ABC):
    def __init__(self, connection: Connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.column_names_string = ""
        self.placeholder_string = ""

    @abstractmethod
    def insert(self, values):
        ...

    @abstractmethod
    def select_one(self):
        ...

    @abstractmethod
    def select_all(self):
        ...