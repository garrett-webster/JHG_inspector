import re
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

    def get_next_game_id(self):
        if self.cursor:
            self.cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'games';")
            row = self.cursor.fetchone()
            if row is None or row[0] is None:
                return 1
            return row[0] + 1

    def load_games(self, folder_path, base_path=None):
        game_paths = [f for f in Path(folder_path).iterdir() if f.is_file()]

        for game_path in game_paths:
            try:
                self.add_game(game_path, base_path=base_path)
            except FileNotFoundError:
                print(f"Could not find game {game_path}")


    def add_game(self, game_path: PosixPath, base_path=None):
        self.games[len(self.games)] = Game(self.connection, game_path, base_path)
