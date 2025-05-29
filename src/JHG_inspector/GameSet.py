import sqlite3
from pathlib import Path

from src.JHG_inspector.DB_commands.DB_init import initialize_DB
from src.JHG_inspector.Game import Game


FILE_PATH = Path(__file__).resolve().parent


class GameSet:
    def __init__(self, name, base_path=FILE_PATH):
        self.games = {}
        self.name = name
        self.connection = None

        self.connect(name, base_path)


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def connect(self, name, base_path):
        # Probably should be handled at the GUI level, but if the db file already exists, we probably want to confirm the name (so as to not overwrite data)
        # Connect to the database
        db_path = base_path / "data_bases" / f"gameset_{name}.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(str(db_path))
        self.connection.execute("PRAGMA foreign_keys = ON")

        initialize_DB(self.connection)

    def load_games(self, folder_path, base_path=None):
        game_paths = [f for f in Path(folder_path).iterdir() if f.is_file()]

        for game_path in game_paths:
            # TODO: Add a try catch here to catch if the file is not found.
            self.add_game(Game(game_path, self.connection, base_path))

    def add_game(self, game: Game):
        self.games[game.code] = game