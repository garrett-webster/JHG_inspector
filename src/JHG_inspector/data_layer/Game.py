import re
from pathlib import Path

from src.JHG_inspector.data_layer.game_file_loaders.GameFileLoader_JsonV1 import GameFileLoader_JsonV1

FILE_PATH = Path(__file__).resolve().parent

class Game:
    def __init__(self, connection, base_path=FILE_PATH):
        self.id = None
        self.connection = connection
        self.cursor = connection.cursor()
        self.id_to_name = {}
        self.name_to_id = {}
        self.code = None

    # Determine the version of the json file and return the correct GameFileLoader for that version
    def create_game_file_loader(self):
        return GameFileLoader_JsonV1(self)

    def load_from_database(self, game_id):
        self.cursor.execute("SELECT code FROM games WHERE id = ?", (game_id,))
        self.code = self.cursor.fetchone()[0]
        print(f"Loading game {self.code} from the database...")
        self.id = game_id
        self.set_id_to_name_dicts()

    def load_from_file(self, game_path):
        self.code = re.match(r"jhg_(.+)\.json", game_path.name).group(1)
        print(f"Adding game {self.code} to the database...")

        self.cursor.execute("SELECT id FROM games WHERE code = ?", (self.code,))
        result = self.cursor.fetchone()
        if result is None:
            # Find the next id (which will be this game's id) and set self.id to it
            self.cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'games';")
            row = self.cursor.fetchone()
            self.id = (row[0] if row and row[0] is not None else 0) + 1
            file_loader = self.create_game_file_loader()
            file_loader.load_data_from_file(game_path)
        else:
            self.id = result[0]
            print(f"Game {self.code} already exists")

    def set_id_to_name_dicts(self):
        # Set up the id_to_name_dict
        self.cursor.execute("SELECT id, gameName FROM players WHERE gameId = ?", (self.id,))
        results = self.cursor.fetchall()

        for result in results:
            self.id_to_name[result[0]] = result[1]
            self.name_to_id[result[1]] = result[0]

class AlreadyExistsError(Exception):
    pass