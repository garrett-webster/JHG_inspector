import json
import re
import sqlite3
from pathlib import Path

from src.JHG_inspector.JSON_STRUCTURE import SIMPLE_JSON_STRUCTURE

FILE_PATH = Path(__file__).resolve().parent

PLAYER_COLUMNS = ["name", "experience", "permissionLevel", "color", "hue", "avatar", "icon"]
PLAYER_COLUMN_TYPES = {
    "name": "TEXT",
    "experience": "INTEGER",
    "permissionLevel": "INTEGER",
    "color": "TEXT",
    "hue": "REAL",
    "avatar": "TEXT",
    "icon": "TEXT"
}


class Game:
    def __init__(self, game_path, base_path=FILE_PATH):
        self.path = game_path
        self.id_to_name_dict = {}
        self.initialized = False

        if not game_path.is_file():
            raise FileNotFoundError

        self.code = re.match(r"jhg_(.+)\.json", game_path.name).group(1)
        self.db_path = base_path / "data_bases" / f"jhg_{self.code}.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Connect to the database
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()

        # If the database has already been initialized, reconstruct the id_to_name_dict
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players';")
        if self.cursor.fetchone():
            self.initialized = True
            self.cursor.execute("SELECT id, name FROM players")
            results = self.cursor.fetchall()

            for result in results:
                self.id_to_name_dict[result[0]] = result[1]


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

    def load_data_to_database(self):
        with open(self.path, "r") as game_file:
            data = json.load(game_file)

        self._load_player_data(data)
        self._load_metadata_and_config(data)
        self.connection.commit()

    def _flatten_dictionary(self, structure, data, parent_key=""):
        values = []
        keys = []
        types = []
        for key, val_type in structure.items():
            full_key = f"{parent_key}_{key}" if parent_key else key
            if isinstance(val_type, dict):
                sub_values, sub_keys, sub_types = self._flatten_dictionary(val_type, data[key], full_key)
                values += sub_values
                keys += sub_keys
                types += sub_types
            else:
                values.append(data[key])
                keys.append(full_key)
                types.append(val_type)
        return values, keys, types

    def _load_player_data(self, data):
        columns_def = "id INTEGER PRIMARY KEY, " + ", ".join(f"{col} {PLAYER_COLUMN_TYPES[col]}" for col in PLAYER_COLUMNS)
        columns_sql = ", ".join(PLAYER_COLUMNS)
        placeholders = ", ".join(["?"] * (len(PLAYER_COLUMNS)))

        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS players ({columns_def})")

        player_values = []
        for i, entry in enumerate(data["players"]):
            player_values.append(tuple(entry[col] for col in PLAYER_COLUMNS))
            self.id_to_name_dict[i + 1] = entry["name"]

        self.cursor.executemany(
            f"INSERT INTO players ({columns_sql}) VALUES ({placeholders})",
            player_values
        )

    def _load_metadata_and_config(self, data):
        for table_name, structure in SIMPLE_JSON_STRUCTURE.items():
            values, keys, types = self._flatten_dictionary(structure, data[table_name])
            columns_sql = ", ".join(keys)
            columns_def = ", ".join(f"{k} {t}" for k, t in zip(keys, types))
            placeholders = ", ".join(["?"] * len(keys))

            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})")
            self.cursor.execute(f"INSERT INTO {table_name} ({columns_sql}) VALUES ({placeholders})", values)

    def _load_playerRoundInfo_data(self, data):
        all_rounds = data["playerRoundInfo"]
        insert_queries = []
        for round_num, round_data in enumerate(all_rounds): # Loop through each round
            for player_name, player_round_data in round_data.items(): # Loop through each player
                # Add relevant data
                insert_queries.append((round_num, player_name, ))
