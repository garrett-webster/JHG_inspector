from pathlib import Path, PosixPath

from src.JHG_inspector.data_layer.Game import Game


FILE_PATH = Path(__file__).resolve().parent

# I might want to add a permanent/temporary flag (or maybe visible) to allow for a tool to clone a gameset and add games temporarily without making it persistent
class GameSet:
    def __init__(self, name, connection, base_path=FILE_PATH):
        self.games = {}
        self.name = name
        self.connection = connection
        self.cursor = connection.cursor()

        # Create the gameset record in the DB (essential to track ids correctly)
        self.cursor.execute(
            "INSERT INTO gamesets (name) VALUES (?)",
            (name, )
        )
        self.id = self.cursor.lastrowid

    def load_games(self, folder_path, base_path=None):
        game_paths = [f for f in Path(folder_path).iterdir() if f.is_file()]

        for game_path in game_paths:
            self.add_game(game_path, base_path=base_path)

        self.connection.commit()

    def add_game(self, game_path: PosixPath, base_path=None):
        new_game = Game(self.connection, game_path, base_path)
        self.games[len(self.games)] = new_game

        self.cursor.execute("INSERT INTO gameset_games (gamesetId, gameId) VALUES (?, ?)", (self.id,new_game.id))
