import sqlite3
from pathlib import Path

from src.JHG_inspector.data_layer.DB_commands.DB_init import initialize_DB
from src.JHG_inspector.data_layer.GameSet import GameSet

FILE_PATH = Path(__file__).resolve().parent

class DatabaseAccess:
    def __init__(self, base_path=FILE_PATH):
        self.gamesets = {}
        self.connection = None
        self.cursor = None
        self.connect(base_path)

    @property
    def games(self):
        games = {}
        for gameset in self.gamesets.values():
            for game_id, game in gameset.games.items():
                games[game_id] = game

        return games

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
        self.load_gamesets_from_database()

    def load_gamesets_from_database(self):
        self.cursor.execute("SELECT id FROM gamesets")
        gameset_ids = self.cursor.fetchall()

        for gameset_id in gameset_ids:
            new_gameset = GameSet(gameset_id[0], self.connection, self.send_gameset_update)
            new_gameset.load_games_from_database()
            self.gamesets[new_gameset.id] = new_gameset

    def create_gameset(self, name):
        self.cursor.execute(
            "INSERT INTO gamesets (name) VALUES (?)",
            (name, )
        )
        new_gameset_id = self.cursor.lastrowid
        new_gameset = GameSet(new_gameset_id, self.connection, self.send_gameset_update)
        self.gamesets[new_gameset.id] = new_gameset

        return new_gameset

    def send_gameset_update(self, gameset_id):
        # Placeholder. This will tie into a ToolsManager object
        print("HEY!")
