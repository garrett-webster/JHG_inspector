import sqlite3
from pathlib import Path, PosixPath

from src.JHG_inspector.data_layer.DB_commands.DB_init import initialize_DB
from src.JHG_inspector.data_layer.Game import Game
from src.JHG_inspector.data_layer.Gameset import Gameset

FILE_PATH = Path(__file__).resolve().parent

class DatabaseAccess:
    def __init__(self, base_path=FILE_PATH):
        self.games = {}
        self.gamesets = {}
        self.connection = None
        self.cursor = None
        self.connect(base_path)

    def __enter__(self, base_path=FILE_PATH):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    # TODO: Set this up to be able to connect to a different data base, closing the previous connection if one exists
    def connect(self, base_path):
        # Probably should be handled at the GUI level, but if the db file already exists, we probably want to confirm the name (so as to not overwrite data)
        # Connect to the database
        db_path = base_path / "data_bases" / f"JHGInspector.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(str(db_path))
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()

        initialize_DB(self.connection)
        self.load_games()
        self.load_gamesets()

    def load_gamesets(self):
        self.gamesets = {}
        self.cursor.execute("SELECT id FROM gamesets")
        gameset_ids = self.cursor.fetchall()

        for gameset_id in gameset_ids:
            new_gameset = Gameset(gameset_id[0], self)
            new_gameset.load_games()
            self.gamesets[new_gameset.id] = new_gameset

    def load_games(self):
        self.games = {}
        self.cursor.execute('SELECT id FROM games')
        game_ids = self.cursor.fetchall()
        for game_id in game_ids:
            game = Game(self.connection)
            game.load_from_database(game_id[0])
            self.games[game_id[0]] = game

    def create_gameset(self, name):
        self.cursor.execute(
            "INSERT INTO gamesets (name) VALUES (?)",
            (name, )
        )
        new_gameset_id = self.cursor.lastrowid
        new_gameset = Gameset(new_gameset_id, self)
        self.gamesets[new_gameset.id] = new_gameset

        return new_gameset

    def delete_gameset(self, gameset: Gameset):
        self.cursor.execute("DELETE FROM gameset_games WHERE gamesetId = ?", (gameset.id,))
        self.cursor.execute("DELETE FROM gamesets WHERE id = ?", (gameset.id,))
        del self.gamesets[gameset.id]

    def load_games_from_directory(self, folder_path, base_path=None, gameset: Gameset = None):
        game_paths = [f for f in folder_path.iterdir() if f.is_file()]
        new_games = []

        for game_path in game_paths:
            new_games.append(self.load_game_from_file(game_path, base_path=base_path))
        self.connection.commit()

        if gameset:
            for game in new_games:
                gameset.add_game(game.id)

    def load_game_from_file(self, game_path: PosixPath, base_path=None):
        new_game = Game(self.connection, base_path)
        new_game.load_from_file(game_path)
        self.games[new_game.id] = new_game

        return new_game

    def send_gameset_update(self, gameset_id):
        # Placeholder. This will tie into a ToolsManager object
        ...