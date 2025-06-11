import json
import re
from abc import ABC, abstractmethod
from pathlib import Path

from src.JHG_inspector.data_layer.DB_commands.DB_init import TableData

"""Loads the data from the game file in to the table that corresponds with the table_name passed to the load_data decorator
   The passed function will compile the values for each row in that table. This function gets the table meta data that the
   decorated function needs to compile the data, then does the insertion operations into the data base"""

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


class GameFileLoader(ABC):
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

    @load_data("games")
    def _load_games_data(self, data, values, table_name):
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

            data["gameParams"]["popularityRandomizationParams"]["randomPopularities"],
            data["gameParams"]["popularityRandomizationParams"]["randomPopHigh"],
            data["gameParams"]["popularityRandomizationParams"]["randomPopLow"],

            data["gameParams"]["governmentParams"]["sendVotesImmediately"],
            data["gameParams"]["labels"]["enabled"],
            data["endCondition"]["duration"],
            data["endCondition"]["runtimeType"],
        ))

    @load_data("searchTags")
    def _load_searchTags_data(self, data, values, table_name):
        for tag, value in data["gameParams"]["show"].items():
            values.append((self.game.id, "show_" + tag, value))

        for tag, value in data["gameParams"]["allowEdit"].items():
            values.append((self.game.id, "allowEdit_" + tag, value))

    @load_data("players")
    def _load_player_data(self, data, values, table_name):
        for entry in data[table_name]:
            values.append((self.game.id, entry["gameName"], entry["name"], entry["experience"], entry["permissionLevel"],
                           entry["color"], entry["hue"], entry["avatar"], entry["icon"]))

    @load_data("admins")
    def _load_admins_data(self, data, values, table_name):
        for game_name in data["lobby"]["admins"]:
            admin_id = self.game.name_to_id[game_name]
            values.append((self.game.id, game_name, admin_id))

    @load_data("playersThatWillBeGovernment")
    def _load_playersThatWillBeGovernment_data(self, data, values, table_name):
        if data["gameParams"]["governmentParams"]["playersThatWillBeGovernment"] is not None:
            for name in data["gameParams"]["governmentParams"]["playersThatWillBeGovernment"]:
                self.game.cursor.execute("SELECT id FROM players WHERE name = ? AND gameId = ?", (name, self.game.id))
                player_id = self.game.cursor.fetchone()
                values.append((self.game.id, player_id[0]))

        self.game.set_id_to_name_dicts()

    @load_data("colorGroups")
    def _load_colorGroups_data(self, data, values, table_name):
        if data.get("colorGroups") is not None:
            for color_group in data["colorGroups"]:
                values.append((self.game.id, color_group["percentOfPlayers"], color_group["color"]))

    @load_data("transactions")
    def _load_transactions_data(self, data, values, table_name):
        for round_num, (round_name, round_transactions) in enumerate(data[table_name].items()):
            for player_from, transactions in round_transactions.items():
                player_from_id = self.game.name_to_id[player_from]
                for player_to, allocation in transactions.items():
                    player_to_id = self.game.name_to_id[player_to]
                    values.append((self.game.id, round_num + 1, player_from_id, player_to_id, allocation))

    @load_data("popularities")
    def _load_popularities_data(self, data, values, table_name):
        for round_num, (round_name, round_data) in enumerate(data[table_name].items()):
            for player, popularity in round_data.items():
                player_id = self.game.name_to_id[player]
                values.append((self.game.id, round_num + 1, player_id, popularity))

    @load_data("groups")
    def _load_groups_data(self, data, values, table_name):
        for round_num, (round_name, round_data) in enumerate(data[table_name].items()):
            values.append((self.game.id, round_num + 1, round_name))

    @load_data("influences")
    def _load_influences_data(self, data, values, table_name):
        for round_num, (round_name, round_transactions) in enumerate(data[table_name].items()):
            for player_from, influences in round_transactions.items():
                player_from_id = self.game.name_to_id[player_from]
                for player_to, influence in influences.items():
                    if player_to != "__intrinsic__":
                        player_to_id = self.game.name_to_id[player_to]
                        values.append((self.game.id, round_num + 1, player_from_id, player_to_id, influence))

    @load_data("chatInfo")
    def _load_chatInfo_data(self, data, values, table_name):
        for in_game_id, chat_info in data[table_name].items():
            values.append((self.game.id, in_game_id, chat_info["name"]))

    @load_data("chatParticipants")
    def  _load_chatParticipants_data(self, data, values, table_name):
        game_id = self.game.id
        for chat_name, chat_info in data["chatInfo"].items():
            chat_id = self.game.cursor.execute(
                "SELECT id FROM chatInfo WHERE inGameId = ? AND gameId = ?",
                (chat_name, game_id)
            ).fetchone()[0]

            if chat_name == "global":
                for player_id in self.game.id_to_name.keys():
                    values.append((chat_id, player_id))
            else:
                for participant in chat_info["participants"]:
                    participant_id = self.game.name_to_id[participant]
                    values.append((chat_id, participant_id))

    @load_data("messages")
    def _load_messages_data(self, data, values, table_name):
        game_id = self.game.id
        for chat_name, chat_info in data["chatInfo"].items():
            chat_id = self.game.cursor.execute(
                "SELECT id FROM chatInfo WHERE inGameId = ? AND gameId = ?",
                (chat_name, game_id)
            ).fetchone()[0]

            for in_game_id, message in chat_info["messages"].items():
                if "from" not in message: message["from"] = None
                values.append((chat_id, in_game_id, message["from"], message["body"], message["time"], message["runtimeType"]))