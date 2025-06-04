import sqlite3
from pathlib import Path

from src.JHG_inspector.DB_commands.DB_init import initialize_DB

FILE_PATH = Path(__file__).resolve().parent

class JHGInspector:
    def __init__(self, base_path=FILE_PATH):
        self.games = {}
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

    def connect(self, base_path):
        # Probably should be handled at the GUI level, but if the db file already exists, we probably want to confirm the name (so as to not overwrite data)
        # Connect to the database
        db_path = base_path / "data_bases" / f"JHGInspector.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(str(db_path))
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()

        initialize_DB(self.connection)