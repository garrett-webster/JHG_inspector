import json
import re
import sqlite3
from pathlib import Path

from src.JHG_inspector.JSON_STRUCTURE import SIMPLE_JSON_STRUCTURE
from src.JHG_inspector.schema_definitions import GAME_SCHEMA_QUERIES

FILE_PATH = Path(__file__).resolve().parent


class Game:
    # base_path allows the tests to safely set up and tear down temporary paths.
    def __init__(self, game_path, base_path=FILE_PATH):
        self.path = game_path

        if not game_path.is_file():
            raise FileNotFoundError

        self.code = re.match(r"jhg_(.+)\.json", game_path.name).group(1)
        self.db_path = base_path / "data_bases" / f"jhg_{self.code}.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = None
        self.cursor = None

        needs_init = not self.db_path.is_file()
        self.connect_to_database()
        if needs_init:
            self.init_database()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def tables_exist(self):
        self.cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='players';
        """)
        return bool(self.cursor.fetchone())

    def connect_to_database(self):
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()

    def init_database(self):
        for query in GAME_SCHEMA_QUERIES.values():
            self.cursor.execute(query)
        self.connection.commit()

        self.connection.commit()

    def load_data_to_database(self):
        with open(self.path, "r") as game_file:
            data = json.load(game_file)

        # Loads the player data in from the "players" dictionary
        player_columns = ["name", "experience", "permissionLevel", "color", "hue", "avatar", "icon"]
        for entry in data["players"]:
            values = tuple(entry[column] for column in player_columns)
            columns_str = ", ".join(player_columns)
            placeholders_str = ", ".join(["?"] * len(player_columns))
            self.cursor.execute(
                f"INSERT INTO players ({columns_str}) VALUES ({placeholders_str})",
                values
            )

        # Flattens a nested dictionary that ends up just being key-value pairs (no lists or anything other than dicts)
        def _flatten_dictionary(to_flatten, data, parent_key=""):
            values = []
            keys = []
            for key, value in to_flatten.items():
                full_key = f"{parent_key}_{key}" if parent_key else key
                if isinstance(value, dict):
                    sub_values, sub_keys = _flatten_dictionary(value, data[key], full_key)
                    values += sub_values
                    keys += sub_keys
                else:
                    values.append(data[key])
                    keys.append(full_key)
            return values, keys

        # Loads most of the game meta-data. See JSON_STRUCTURE.py to see exactly which once
        for table, columns in SIMPLE_JSON_STRUCTURE.items():
            values, columns = _flatten_dictionary(SIMPLE_JSON_STRUCTURE[table], data[table])
            columns_str = ", ".join(columns)
            placeholders_str = ", ".join(["?"] * len(columns))
            self.cursor.execute(
                f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders_str})",
                values
            )
        self.connection.commit()