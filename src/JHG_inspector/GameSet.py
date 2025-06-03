from pathlib import Path, PosixPath

from src.JHG_inspector.Game import Game


FILE_PATH = Path(__file__).resolve().parent


class GameSet:
    def __init__(self, name, connection, gameset_id, base_path=FILE_PATH):
        self.games = {}
        self.name = name
        self.connection = connection
        self.cursor = connection.cursor()
        self.id = gameset_id

        # Create the gameset record in the DB (essential to track ids correctly)
        self.cursor.execute(
            "INSERT INTO gamesets (name) VALUES (?)",
            (name, )
        )

    def load_games(self, folder_path, base_path=None):
        game_paths = [f for f in Path(folder_path).iterdir() if f.is_file()]

        for game_path in game_paths:
            self.add_game(game_path, base_path=base_path)

    def add_game(self, game_path: PosixPath, base_path=None):
        self.games[len(self.games)] = Game(self.connection, game_path, base_path)
