import re
from pathlib import Path

from src.JHG_inspector.data_layer.game_file_loaders.GameFileLoader import GameFileLoader

FILE_PATH = Path(__file__).resolve().parent

class Game:
    def __init__(self, connection, game_path, base_path=FILE_PATH):
        self.connection = connection
        self.cursor = connection.cursor()
        self.id_to_name = {}
        self.name_to_id = {}
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
            file_loader = self.create_game_file_loader()
            file_loader.load_data_from_file(game_path)

    def create_game_file_loader(self):
        return GameFileLoader(self)

    def set_id_to_name_dicts(self):
        # Set up the id_to_name_dict
        self.cursor.execute("SELECT id, gameName FROM players WHERE gameId = ?", (self.id,))
        results = self.cursor.fetchall()

        for result in results:
            self.id_to_name[result[0]] = result[1]
            self.name_to_id[result[1]] = result[0]







