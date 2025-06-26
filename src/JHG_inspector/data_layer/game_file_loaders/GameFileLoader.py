import json
import re
from pathlib import Path, PosixPath

from src.JHG_inspector.data_layer.DatabaseManager import DatabaseManager
from src.JHG_inspector.old_data_layer.DB_commands.DB_init import TableData

NUM_LOAD_FUNCTIONS = 0


def load_data(table_name: str = None):
    """Decorator that automates getting the schema for the table with the passed table_name and inserting that data.

       Loads the data from the game file in to the table that corresponds with the table_name passed to the load_data
       decorator The passed function will compile the values for each row in that table. This function gets the table
       metadata that the decorated function needs to compile the data, then does the insertion operations into the
       database.

       To use a function decorated with load_data, pass a string with the name of the database table you want to insert
       into load_data (the decoration will look like @load_data("tableName")). The decorated function must take
       (self, data, values, table_name) as its arguments. Then, do logic needed to collect the values that should be
       inserted into the given table and call values.append(), passing it a tuple with the values in the order defined
       in the schema for that table (see src/data_layer/DB_commands/schema.json)
       """

    def decorator(function):
        global NUM_LOAD_FUNCTIONS

        def wrapper(self, data):
            if table_name is not None:
                values = []
                function(self, data, values, table_name)

                self.database_manager.DAOs[table_name].insert(values)

        # Marks the functions so that they can be collected and run later on
        wrapper._load_function_order = NUM_LOAD_FUNCTIONS
        NUM_LOAD_FUNCTIONS += 1
        return wrapper

    return decorator


class GameFileLoader:
    """Base class for game file loading.

       Each subclass defines the functions necessary to load the data from a different version of the json, allowing
       updates to the json to not break existing datasets. These methods (in the subclass) are decorated with
       @load_data, which marks them to be run by load_data_from_file. They are run in the order that they are declared,
       which allows for control of call order for handling dependencies (especially the creation of the name_to_id and
       id_to_name dictionaries)
       """

    def __init__(self, database_manager: DatabaseManager, game: "Game"):
        """
        Parameters
        ----------
        game : JHG_inspector.data_layer.Game
            A Game object that will hold the data read from the file
        """
        self.game = game
        self.database_manager = database_manager
        self.connection = database_manager.connection
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

    def load_data_from_file(self, game_path: PosixPath):
        """Runs all the functions annotated with @load_data, passing in the data loaded from the passed game_path file.

        Parameters
        ----------
        game_path: PosixPath
            The path of the game file to load
        """

        if not game_path.is_file():
            raise FileNotFoundError

        self.game.code = re.match(r"jhg_(.+)\.json", game_path.name).group(1)

        with open(game_path, "r") as game_file:
            data = json.load(game_file)

        for _, func in self._load_functions:
            func(data)

        self.connection.commit()