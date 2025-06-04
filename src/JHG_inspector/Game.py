import json
import re
from pathlib import Path

from src.JHG_inspector.DB_commands.DB_init import get_schema, TableData

FILE_PATH = Path(__file__).resolve().parent

"""Loads the data from the game file in to the table that corresponds with the table_name passed to the load_data decorator
   The passed function will compile the values for each row in that table. This function gets the table meta data that the
   decorated function needs to compile the data, then does the insertion operations into the data base"""
def load_data(table_name: str):
    def decorator(function):
        def wrapper(self, data):
            columns, column_names, placeholders = self._prepare_sql_strings(table_name)
            values = []

            function(self, data, values, table_name)

            self.cursor.executemany(
                f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})",
                values
            )
        return wrapper
    return decorator


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

        self._load_games_data(data)
        self._load_player_data(data)
        self.set_id_to_name_dicts()

        self._load_transactions_data(data)
        self._load_popularities_data(data)
        self._load_influences_data(data)
        self.connection.commit()

    # def _load_metadata_and_config(self, data):
    #     # Minimum insert to get the ids tracking correctly
    #     code = data["lobby"]["code"]
    #     self.cursor.execute(
    #         "INSERT INTO games (code) VALUES (?)",
    #         (code,)
    #     )

    @load_data("games")
    def _load_games_data(self, data, values, table_name):
        # There are circular dependencies with doing this. This relies on name_to_id which relies on the id existing.
        # creatorId = self.name_to_id[data["lobby"]["creatorName"]] if data["lobby"]["creatorName"] is not None else None

        values.append((
            data["lobby"]["code"],
            data["lobby"]["numPlayers"],
            data["lobby"]["numObservers"],
            data["status"],
            # creatorId,
            data["startDateTime"],
            data["gameParams"]["lengthOfRound"],
            data["gameParams"]["nameSet"],
            data["gameParams"]["chatType"],
            data["gameParams"]["messageType"],
            data["gameParams"]["advancedGameSetup"],
            data["gameParams"]["gameEndCriteria"]["low"],
            data["gameParams"]["gameEndCriteria"]["high"],
            data["gameParams"]["gameEndCriteria"]["runtimeType"],
            data["gameParams"]["popularityFunctionParams"]["alpha"],
            data["gameParams"]["popularityFunctionParams"]["beta"],
            data["gameParams"]["popularityFunctionParams"]["cGive"],
            data["gameParams"]["popularityFunctionParams"]["cKeep"],
            data["gameParams"]["popularityFunctionParams"]["cSteal"],
            data["gameParams"]["popularityFunctionParams"]["povertyLine"],
            data["gameParams"]["governmentParams"]["initialPopularity"],
            data["gameParams"]["governmentParams"]["initialPopularityType"],
            data["gameParams"]["governmentParams"]["randomPopularities"],
            data["gameParams"]["governmentParams"]["randomPopHigh"],
            data["gameParams"]["governmentParams"]["randomPopLow"],
            data["gameParams"]["governmentParams"]["sendVotesImmediately"],
            data["gameParams"]["labels"]["enabled"],
            data["endCondition"]["duration"],
            data["endCondition"]["runtimeType"],
        ))

    @load_data("players")
    def _load_player_data(self, data, values, table_name):
        for entry in data[table_name]:
            values.append((self.id, entry["gameName"], entry["name"], entry["experience"], entry["permissionLevel"],
                           entry["color"], entry["hue"], entry["avatar"], entry["icon"]))

    @load_data("transactions")
    def _load_transactions_data(self, data, values, table_name):
        for round_num, (round_name, round_transactions) in enumerate(data[table_name].items()):
            for player_from, transactions in round_transactions.items():
                player_from_id = self.name_to_id[player_from]
                for player_to, allocation in transactions.items():
                    player_to_id = self.name_to_id[player_to]
                    values.append((self.id, round_num + 1, player_from_id, player_to_id, allocation))

    @load_data("popularities")
    def _load_popularities_data(self, data, values, table_name):
        for round_num, (round_name, round_data) in enumerate(data[table_name].items()):
            for player, popularity in round_data.items():
                player_id = self.name_to_id[player]
                values.append((self.id, round_num + 1, player_id, popularity))

    @load_data("influences")
    def _load_influences_data(self, data, values, table_name):
        for round_num, (round_name, round_transactions) in enumerate(data[table_name].items()):
            for player_from, influences in round_transactions.items():
                player_from_id = self.name_to_id[player_from]
                for player_to, influence in influences.items():
                    if player_to != "__intrinsic__":
                        player_to_id = self.name_to_id[player_to]
                        values.append((self.id, round_num + 1, player_from_id, player_to_id, influence))

    def _prepare_sql_strings(self, table_name: str):
        table_data = TableData(self.schema[table_name])
        columns = table_data.non_excluded_columns
        if table_name == "games":
            column_names = ", ".join([column[0] for column in columns])
            placeholders = ", ".join(["?" for _ in columns])
        else:
            column_names = ", ".join(["gameId"] + [column[0] for column in columns])
            placeholders = ", ".join(["?"] + ["?" for _ in columns])

        return columns, column_names, placeholders
