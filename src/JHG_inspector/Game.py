import json
import re
from pathlib import Path

from src.JHG_inspector.DB_commands.DB_init import get_schema, TableData

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
    def __init__(self, game_path, connection, game_id, gameset_id, base_path=FILE_PATH):
        self.path = game_path
        self.id_to_name_dict = {}
        self.initialized = False
        self.connection = connection
        self.cursor = connection.cursor()
        self.schema = get_schema(self.cursor)
        self.id = game_id
        self.gameset_id = gameset_id

        if not game_path.is_file():
            raise FileNotFoundError

        self.code = re.match(r"jhg_(.+)\.json", game_path.name).group(1)


        # # If the database has already been initialized, reconstruct the id_to_name_dict
        # self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players';")
        # if self.cursor.fetchone():
        #     self.initialized = True
        #     self.cursor.execute("SELECT id, name FROM players")
        #     results = self.cursor.fetchall()
        #
        #     for result in results:
        #         self.id_to_name_dict[result[0]] = result[1]

        self.load_data_to_database()

    def load_data_to_database(self):
        with open(self.path, "r") as game_file:
            data = json.load(game_file)

        self._load_metadata_and_config(data)
        self._load_player_data(data)
        # self._load_playerRoundInfo_data(data)
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
        table_data = TableData(self.schema["players"])
        player_columns = table_data.non_key_columns
        player_values = []


        column_names = ", ".join(["gameId"] + [column[0] for column in player_columns])
        placeholders = ", ".join(["?"] + ["?" for _ in player_columns])
        for i, entry in enumerate(data["players"]):
            player_values.append((self.id, ) + tuple(entry[col[0]] for col in player_columns))
            self.id_to_name_dict[i + 1] = entry["name"]

        self.cursor.executemany(
            f"INSERT INTO players ({column_names}) VALUES ({placeholders})",
            player_values
        )

    def _load_metadata_and_config(self, data):
        # table_data = TableData(self.schema["games"])
        # columns = table_data.non_key_columns


        # Minimum insert to get the ids tracking correctly
        code = data["lobby"]["code"]
        self.cursor.execute(
            "INSERT INTO games (gamesetId, code) VALUES (?, ?)",
            (self.gameset_id, code)
        )


    def _load_playerRoundInfo_data(self, data):
        all_rounds = data["playerRoundInfo"]
        insert_queries = []
        for round_num, round_data in enumerate(all_rounds): # Loop through each round
            for player_name, player_round_data in all_rounds[round_data].items(): # Loop through each player
                # Add relevant data
                insert_queries.append((round_num, player_name, ))
