import json
import re
from functools import cached_property
from pathlib import Path, PosixPath

from src.JHG_inspector.data_layer.game_file_loaders.GameFileLoader_JsonV1 import GameFileLoader_JsonV1
from src.JHG_inspector.data_layer.game_file_loaders.game_file_loader_versions import VERSION_TO_GAME_FILE_LOADER

FILE_PATH = Path(__file__).resolve().parent

class Game:
    """Holds the data for a single game."""
    def __init__(self, database_manager: "DatabaseManager"):
        self.database_manager = database_manager
        self.id_to_name = {}
        self.name_to_id = {}
        self.id_to_player_order = {}
        self.id = None
        self.code = None

    def create_game_file_loader(self, game_log_path: Path):
        """Factory method for game file loaders.

           Determines the version of the game log file and returns a GameFileLoader object of the correct type.
           """
        with open(game_log_path, "r") as game_file:
            data = json.load(game_file)
            version = data["version"]
            return VERSION_TO_GAME_FILE_LOADER[version]

    def load_from_database(self, game_id: int):
        """Find the game record in the database based on the games id and load the data from the database"""

        self.code = self.database_manager.DAOs["games"].select_one(["code"], ["id"], [game_id])[0]
        print(f"Loading game {self.code} from the database...")
        self.id = game_id
        self.set_id_to_name_dicts()

    # TODO: Cache game loader objects (based on JSON version) so you're not creating a new one for each file.
    def load_from_file(self, game_path: Path):
        """Loads a game from a file into the database and the Game object.

           Checks whether a game with the same game code has been loaded into the database yet. If not, find the next
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
            file_loader = self.create_game_file_loader(game_path)(self.database_manager, self, game_path)
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
    @cached_property
    def popularities(self) -> list[list[int]]:
        """Returns the popularitites by player by round.

           Each sub list holds the popularities for one round, where the index is the round number zero indexed. The
           items of each of those lists represents the popularity of the player whos id relates to the index position,
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
           each player j, such that the ijth entry of the matrix in the kth index of influences is player i's influence
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
    def transactions(self) -> list[list[list[int]]]:
        """Returns the allocations from each player to each player by round.

           Each sub list holds a matrix (2-dimensional list) where the rows represent the token allocation from player i
           to each player j, such that the ijth entry of the matrix in the kth index of transaction is player i's token
           allocation to player j on round k.
           """

        results = self.database_manager.DAOs["transactions"].select_all(["*"], ["gameId"], [self.id])
        ids = self.id_to_name.keys()
        num_rounds = int(len(results) / len(ids)**2)
        transactions = [[[0 for _ in range(len(ids))] for _ in range(len(ids))] for _ in range(num_rounds)]

        for result in results:
            round_num = result[1]
            player_from_id = self.id_to_player_order[result[2]]
            player_to_id = self.id_to_player_order[result[3]]
            transaction = result[4]
            transactions[round_num - 1][player_from_id][player_to_id] = transaction

        return transactions