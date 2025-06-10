import json
import re
from pathlib import Path

from src.JHG_inspector.data_layer.DB_commands.DB_init import get_schema, TableData

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
        self._load_searchTags_data(data)
        self._load_player_data(data)
        self._load_admins_data(data)
        self.set_id_to_name_dicts()

        self._load_transactions_data(data)
        self._load_popularities_data(data)
        self._load_influences_data(data)
        self._load_chatInfo_data(data)
        self._load_chatParticipants_data(data)
        self._load_messages_data(data)
        self.connection.commit()

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

    @load_data("searchTags")
    def _load_searchTags_data(self, data, values, table_name):
        for tag, value in data["gameParams"]["show"].items():
            values.append((self.id, "show_" + tag, value))

        for tag, value in data["gameParams"]["allowEdit"].items():
            values.append((self.id, "allowEdit_" + tag, value))

    @load_data("players")
    def _load_player_data(self, data, values, table_name):
        for entry in data[table_name]:
            values.append((self.id, entry["gameName"], entry["name"], entry["experience"], entry["permissionLevel"],
                           entry["color"], entry["hue"], entry["avatar"], entry["icon"]))

    @load_data("admins")
    def _load_admins_data(self, data, values, table_name):
        for game_name in data["lobby"]["admins"]:
            admin_id = self.name_to_id[game_name]
            values.append((self.id, game_name, admin_id))

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

    @load_data("chatInfo")
    def _load_chatInfo_data(self, data, values, table_name):
        for in_game_id, chat_info in data[table_name].items():
            values.append((self.id, in_game_id, chat_info["name"]))

    def  _load_chatParticipants_data(self, data):
        game_id = self.id
        for chat_name, chat_info in data["chatInfo"].items():
            chat_id = self.cursor.execute(
                "SELECT id FROM chatInfo WHERE inGameId = ? AND gameId = ?",
                (chat_name, game_id)
            ).fetchone()[0]
            if chat_name == "global":
                for player_id in self.id_to_name.keys():
                    self.cursor.execute("INSERT INTO chatParticipants (conversationId, playerId) VALUES (?, ?)", (chat_id, player_id))
            else:
                for participant in chat_info["participants"]:
                    participant_id = self.name_to_id[participant]
                    self.cursor.execute("INSERT INTO chatParticipants (conversationId, playerId) VALUES (?, ?)",
                        (chat_id, participant_id))

    def  _load_messages_data(self, data):
        game_id = self.id
        for chat_name, chat_info in data["chatInfo"].items():
            chat_id = self.cursor.execute(
                "SELECT id FROM chatInfo WHERE inGameId = ? AND gameId = ?",
                (chat_name, game_id)
            ).fetchone()[0]


            for in_game_id, message in chat_info["messages"].items():
                if "from" not in message: message["from"] = None
                self.cursor.execute("INSERT INTO messages (conversationId, inGameId, playerFrom, body, time, runtimeType) VALUES (?, ?, ?, ?, ?, ?)",
                    (chat_id, in_game_id, message["from"], message["body"], message["time"], message["runtimeType"]))

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