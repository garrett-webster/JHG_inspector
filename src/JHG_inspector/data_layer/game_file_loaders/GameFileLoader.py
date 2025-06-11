import json
import re
from pathlib import Path

from src.JHG_inspector.data_layer.DB_commands.DB_init import TableData

"""Loads the data from the game file in to the table that corresponds with the table_name passed to the load_data decorator
   The passed function will compile the values for each row in that table. This function gets the table meta data that the
   decorated function needs to compile the data, then does the insertion operations into the data base.
   
   To use a function decorated with load_data, pass a string with the name of the database table you want to insert into
   load_data (the decoration will look like @load_data("tableName")). The decorated function must take 
   (self, data, values, table_name) as its arguments. Then, do logic needed to collect the values that should be
    inserted into the given table and call values.append(), passing it a tuple with the values in the order defined in
    the schema for that table (see src/data_layer/DB_commands/schema.json)"""

NUM_LOAD_FUNCTIONS = 0
def load_data(table_name: str = None):
    def decorator(function):
        global NUM_LOAD_FUNCTIONS

        def wrapper(self, data):
            if table_name is not None:
                columns, column_names, placeholders = self._prepare_sql_strings(table_name)
                values = []

                function(self, data, values, table_name)

                self.cursor.executemany(
                    f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})",
                    values
                )

        wrapper._load_function_order = NUM_LOAD_FUNCTIONS
        NUM_LOAD_FUNCTIONS += 1
        return wrapper

    return decorator


"""Base class for game file loading. Each subclass defines the functions necessary to load the data from a different 
   version of the json, allowing for updates to the json to not break existing datasets. These methods (in the subclass)
   are decorated with @load_data, which marks them to be ran by load_data_from_file. They are run in the order that they
   are declared, which allows for control of call order for handling dependencies (especially the creation of the 
   name_to_id and id_to_name dictionaries)"""


class GameFileLoader:
    def __init__(self, game):
        self.game = game
        self.connection = game.connection
        self.cursor = game.cursor
        with open(Path(__file__).parent.parent / "DB_commands" / "schema.json", "r") as f:
            self.schema = json.load(f)

        # Collect all the functions annotated with @load_data and sort them in order of declaration
        self._load_functions = []
        for attr in dir(self):
            func = getattr(self, attr)
            if callable(func) and hasattr(func, "_load_function_order"):
                self._load_functions.append((func._load_function_order, func))

        # Sort by load order
        self._load_functions.sort(key=lambda x: x[0])

    def _prepare_sql_strings(self, table_name: str):
        table_data = TableData(self.schema[table_name])
        columns = table_data.non_excluded_columns
        if ('gameId', 'INTEGER') in table_data.columns:
            column_names = ", ".join(["gameId"] + [column[0] for column in columns])
            placeholders = ", ".join(["?"] + ["?" for _ in columns])
        else:
            column_names = ", ".join([column[0] for column in columns])
            placeholders = ", ".join(["?" for _ in columns])

        return columns, column_names, placeholders

    def load_data_from_file(self, game_path):
        if not game_path.is_file():
            raise FileNotFoundError

        self.game.code = re.match(r"jhg_(.+)\.json", game_path.name).group(1)

        with open(game_path, "r") as game_file:
            data = json.load(game_file)
        for _, func in self._load_functions:
            func(data)  # or func(self, data) depending on your wrapper

        self.connection.commit()