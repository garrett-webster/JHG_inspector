import json
import re
import sqlite3
from pathlib import Path

from src.JHG_inspector.JSON_STRUCTURE import SIMPLE_JSON_STRUCTURE

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

        self.connect_to_database()

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
                f"CREATE TABLE IF NOT EXISTS players ({columns_str})"
            )
            self.cursor.execute(
                f"INSERT INTO players ({columns_str}) VALUES ({placeholders_str})",
                values
            )

        # Flattens a nested dictionary that ends up just being key-value pairs (no lists or anything other than dicts)
        def _flatten_dictionary(structure, data, parent_key=""):
            values = []
            keys = []
            types = []
            for key, value in structure.items():
                full_key = f"{parent_key}_{key}" if parent_key else key
                if isinstance(value, dict):
                    sub_values, sub_keys, sub_types = _flatten_dictionary(value, data[key], full_key)
                    values += sub_values
                    keys += sub_keys
                    types += sub_types
                else:
                    values.append(data[key])
                    keys.append(full_key)
                    types.append(value)
            return values, keys, types

        # Loads most of the game meta-data. See JSON_STRUCTURE.py to see exactly what is loaded
        for table, columns in SIMPLE_JSON_STRUCTURE.items():
            values, columns, types = _flatten_dictionary(SIMPLE_JSON_STRUCTURE[table], data[table])
            columns_str = ", ".join(columns)
            columns_def_string = ", ".join(f"{col} {typ}" for col, typ in zip(columns, types))

            self.cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {table} ({columns_def_string})"
            )
            self.cursor.execute(
                f"INSERT INTO {table} ({columns_str}) VALUES ({", ".join(["?"] * len(columns))})",
                values
            )
        self.connection.commit()