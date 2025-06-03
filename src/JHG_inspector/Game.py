import json
import re
from pathlib import Path

from src.JHG_inspector.DB_commands.DB_init import get_schema, TableData

FILE_PATH = Path(__file__).resolve().parent


class Game:
    def __init__(self, connection, game_path, base_path=FILE_PATH):
        self.connection = connection
        self.cursor = connection.cursor()
        self.id_to_name = {}
        self.name_to_id = {}
        self.schema = get_schema(self.cursor)
        self.code = re.match(r"jhg_(.+)\.json", game_path.name).group(1)

        # Check if the game already exists in the DB. If not, load the data from the game log
        self.cursor.execute(f"SELECT id FROM games WHERE code = ('{self.code}');")
        result = self.cursor.fetchone()
        if result is not None:
            print(f"Loading game {self.code} from the database...")
            self.id = result[0]
            self.set_id_to_name_dicts()
        else:
            print(f"Adding game {self.code} to the database...")

            # Find the next id (which will be this game's id) and set self.id to it
            self.cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'games';")
            row = self.cursor.fetchone()
            self.id = (row[0] if row and row[0] is not None else 0) + 1

            self.load_data_from_file(game_path)

    def set_id_to_name_dicts(self):
        # Set up the id_to_name_dict
        self.cursor.execute("SELECT id, gameName FROM players WHERE gameId = ?", (self.id,))
        results = self.cursor.fetchall()

        for result in results:
            self.id_to_name[result[0]] = result[1]
            self.name_to_id[result[1]] = result[0]

    def load_data_from_file(self, game_path):
        if not game_path.is_file():
            raise FileNotFoundError

        self.code = re.match(r"jhg_(.+)\.json", game_path.name).group(1)

        with open(game_path, "r") as game_file:
            data = json.load(game_file)

        self._load_metadata_and_config(data)
        self._load_player_data(data)
        self.set_id_to_name_dicts()

        self._load_transactions_data(data)
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

        for entry in data["players"]:
            player_values.append((self.id,) + tuple(entry[col[0]] for col in columns))

        self.cursor.executemany(
            f"INSERT INTO players ({column_names}) VALUES ({placeholders})",
            player_values
        )

    def _load_transactions_data(self, data):
        columns, column_names, placeholders = self._prepare_sql_strings("transactions")
        transaction_values = []

        for round_num, (round_name, round_transactions) in enumerate(data["transactions"].items()):
            for player_from, transactions in round_transactions.items():
                player_from_id = self.name_to_id[player_from]
                for player_to, allocation in transactions.items():
                    player_to_id = self.name_to_id[player_to]
                    transaction_values.append((self.id, round_num + 1, player_from_id, player_to_id, allocation))

        self.cursor.executemany(
            f"INSERT INTO transactions ({column_names}) VALUES ({placeholders})",
            transaction_values
        )


    def _prepare_sql_strings(self, table_name: str):
        table_data = TableData(self.schema[table_name])
        columns = table_data.non_excluded_columns
        column_names = ", ".join(["gameId"] + [column[0] for column in columns])
        placeholders = ", ".join(["?"] + ["?" for _ in columns])

        return columns, column_names, placeholders
