import json
import re
from functools import cached_property
from pathlib import Path
from src.JHG_inspector.data_layer.game_file_loaders.game_file_loader_versions import VERSION_TO_GAME_FILE_LOADER
from src.JHG_inspector.logic_layer.Player import Player
from src.JHG_inspector.logic_layer.Round import Round

FILE_PATH = Path(__file__).resolve().parent


def get_game_file_loader(game_log_path: Path):
    """Factory method for game file loaders.

       Determines the version of the game log file and returns a GameFileLoader object of the correct type. If there
       has already been a GameFileLoader object created for that file version, fetch it. If not, create a new
       instance and cache it.
       """
    with open(game_log_path, "r") as game_file:
        data = json.load(game_file)
        version = data["version"]

    if version in Game.game_file_loaders:
        return Game.game_file_loaders[version]
    else:
        Game.game_file_loaders[version] = VERSION_TO_GAME_FILE_LOADER[version]
        return Game.game_file_loaders[version]


class Game:
    """Holds the data for a single game."""

    game_file_loaders = {}
    def __init__(self, database_manager: "DatabaseManager"):
        self.database_manager = database_manager
        self.id_to_name = {}
        self.name_to_id = {}
        self.num_rounds: int
        self.id_to_player_order = {}
        self.id = None
        self.code = None

    def load_from_database(self, game_id: int):
        """Find the game record in the database based on the games id and load the data from the database"""

        self.code = self.database_manager.DAOs["games"].select_one(["code"], ["id"], [game_id])[0]
        print(f"Loading game {self.code} from the database...")
        self.id = game_id
        self.set_id_to_name_dicts()

    def load_from_file(self, game_path: Path):
        """Loads a game from a file into the database and the Game object.

           Checks whether a game with the same game code has been loaded into the database. If not, find the next
           id, create a GameFileLoader, and load the data from the file.
           """

        self.code = re.match(r"jhg_(.+)\.json", game_path.name).group(1)
        print(f"Adding game {self.code} to the database...")

        result = self.database_manager.DAOs["games"].select_one(["id"], ["code"], [self.code])
        if result is None:
            # Find the next id (which will be this game's id) and set self.id to it
            cursor = self.database_manager.connection.cursor()
            cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'games';")
            row = cursor.fetchone()
            self.id = (row[0] if row and row[0] is not None else 0) + 1

            file_loader = get_game_file_loader(game_path)(self.database_manager, self)
            file_loader.load_data_from_file(game_path)
        else:
            self.id = result[0]
            print(f"Game {self.code} already exists")

    def set_id_to_name_dicts(self):
        """Create the id_to_name and name_to_id dictionaries.

           id_to_name takes a game id from the database and returns the name of the player.
           name_to_id takes a player name and returns the game id from the database.
           """

        results = self.database_manager.DAOs["players"].select_all(["id", "gameName"], ["gameId"], [self.id])

        for i, result in enumerate(results):
            self.id_to_name[result[0]] = result[1]
            self.name_to_id[result[1]] = result[0]
            self.id_to_player_order[result[0]] = i
            
    # !--- Data Methods ---! #
    def simple_dictionary_property(self, columns, table):
        """Utility method that reduces code duplication in the data methods.

           Takes a list of column names and a table and retrieves their values for the game, assigning them to a
           dictionary."""
        property_dict = {}

        results = self.database_manager.DAOs["games"].select_one(columns, ["id"], [self.id])

        for i, column in enumerate(columns):
            property_dict[column] = results[i]

        return property_dict

    @cached_property
    def num_rounds(self) -> int:
        return self.database_manager.DAOs["games"].select_one(["numRounds"], ["id"], [self.id])[0]

    @cached_property
    def num_players(self):
        return self.database_manager.DAOs["games"].select_one(["numPlayers"], ["id"], [self.id])[0]

    @cached_property
    def popularities(self) -> list[list[int]]:
        """Returns the popularitites by player by round.

           Each sub list holds the popularities for one round, where the index is the round number zero indexed. The
           items of each of those lists represent the popularity of the player whose id relates to the index position,
           as stored in self.id_to_player_order.
           """

        results = self.database_manager.DAOs["popularities"].select_all(["*"], ["gameId"], [self.id])
        ids = self.id_to_name.keys()
        num_rounds = int(len(results)/len(ids))
        popularities = [[0 for _ in range(len(ids))] for _ in range(num_rounds)]

        for result in results:
            round_num = result[1]
            player_order_number = self.id_to_player_order[result[2]]
            popularity = result[3]
            popularities[round_num - 1][player_order_number] = popularity

        return popularities

    @cached_property
    def influences(self) -> list[list[list[int]]]:
        """Returns the influence on each player by each player by round.

           Each sub list holds a matrix (2-dimensional list) where the rows represent the influence from player i on
           each player j. Thus, the ijth entry of the matrix in the kth index of influences is player i's influence
           on player j on round k.
           """

        results = self.database_manager.DAOs["influences"].select_all(["*"], ["gameId"], [self.id])
        ids = self.id_to_name.keys()
        num_rounds = int(len(results) / len(ids)**2)
        influences = [[[0 for _ in range(len(ids))] for _ in range(len(ids))] for _ in range(num_rounds)]

        for result in results:
            round_num = result[1]
            player_from_id = self.id_to_player_order[result[2]]
            player_to_id = self.id_to_player_order[result[3]]
            influence = result[4]
            influences[round_num - 1][player_from_id][player_to_id] = influence

        return influences

    @cached_property
    def allocations(self) -> list[list[list[int]]]:
        """Returns the allocations from each player to each player by round.

           Each sub list holds a matrix (2-dimensional list) where the rows represent the token allocation from player i
           to each player j. Thus, the ijth entry of the matrix in the kth index of transaction is player i's token
           allocation to player j on round k.
           """

        results = self.database_manager.DAOs["transactions"].select_all(["*"], ["gameId"], [self.id])
        ids = self.id_to_name.keys()
        num_rounds = int(len(results) / len(ids)**2)
        allocations = [[[0 for _ in range(len(ids))] for _ in range(len(ids))] for _ in range(num_rounds)]

        for result in results:
            round_num = result[1]
            player_from_id = self.id_to_player_order[result[2]]
            player_to_id = self.id_to_player_order[result[3]]
            allocation = result[4]
            allocations[round_num - 1][player_from_id][player_to_id] = allocation

        return allocations

    @cached_property
    def settings(self):
        columns = ["chatType", "messageType", "advancedGameSetup", "gameEndLow", "gameEndHigh", "gameEndType", "povertyLine",
             "govInitialPopularity", "govInitialPopularityType", "govRandomPopularities", "govRandomPopHigh",
             "govRandomPopLow", "govSendVotesImmediately", "labelsEnabled", "duration", "runtimeType"]

        return self.simple_dictionary_property(columns, "games")

    @cached_property
    def parameters(self):
        columns = ["alpha", "beta", "cGive", "cKeep", "cSteal", "lengthOfRound"]

        return self.simple_dictionary_property(columns, "games")

    @cached_property
    def meta_data(self):
        columns = ["numPlayers", "numObservers", "status", "startDateTime"]

        return self.simple_dictionary_property(columns, "games")

    @cached_property
    def rounds(self):
        rounds = []
        for i in range(self.num_rounds):
            rounds.append(Round(self, i))

        return rounds

    @cached_property
    def players(self):
        players = []
        for player_id in self.name_to_id.values():
            player_order_num = self.id_to_player_order[player_id]
            players.append(Player(self, player_id, player_order_num))

        return players

