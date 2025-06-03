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
    def __init__(self, connection, game_path, base_path=FILE_PATH):
        self.connection = connection
        self.cursor = connection.cursor()
        self.id_to_name_dict = {}
        self.schema = get_schema(self.cursor)
        self.code = re.match(r"jhg_(.+)\.json", game_path.name).group(1)

        # Check if the game already exists in the DB. If not, load the data from the game log
        self.cursor.execute(f"SELECT id FROM games WHERE code = ('{self.code}');")
        result = self.cursor.fetchone()
        if result is not None:
            print(f"Loading game {self.code} from the database...")
            self.id = result[0]
        else:
            print(f"Adding game {self.code} to the database...")

            # Find the next id (which will be this game's id) and set self.id to it
            self.cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'games';")
            row = self.cursor.fetchone()
            self.id = (row[0] if row and row[0] is not None else 0) + 1

            self.load_data_from_file(game_path)

        # Set up the id_to_name_dict
        self.cursor.execute("SELECT id, name FROM players WHERE gameId = ?", (self.id,))
        results = self.cursor.fetchall()

        for result in results:
            self.id_to_name_dict[result[0]] = result[1]

    def load_data_from_file(self, game_path):
        if not game_path.is_file():
            raise FileNotFoundError

        self.code = re.match(r"jhg_(.+)\.json", game_path.name).group(1)

        with open(game_path, "r") as game_file:
            data = json.load(game_file)

        self._load_metadata_and_config(data)
        self._load_player_data(data)
        self.connection.commit()

    def _load_metadata_and_config(self, data):
        # table_data = TableData(self.schema["games"])
        # columns = table_data.non_key_columns

        # Minimum insert to get the ids tracking correctly
        code = data["lobby"]["code"]
        self.cursor.execute(
            "INSERT INTO games (code) VALUES (?)",
            (code,)
        )

    def _load_player_data(self, data):
        columns, column_names, placeholders = self._prepare_sql_strings("players")
        player_values = []

        for i, entry in enumerate(data["players"]):
            player_values.append((self.id,) + tuple(entry[col[0]] for col in columns))
            self.id_to_name_dict[i + 1] = entry["name"]

        self.cursor.executemany(
            f"INSERT INTO players ({column_names}) VALUES ({placeholders})",
            player_values
        )

    def _prepare_sql_strings(self, table_name: str):
        table_data = TableData(self.schema[table_name])
        columns = table_data.non_key_columns
        column_names = ", ".join(["gameId"] + [column[0] for column in columns])
        placeholders = ", ".join(["?"] + ["?" for _ in columns])

        return columns, column_names, placeholders
