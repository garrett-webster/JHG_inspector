import sqlite3
from pathlib import Path


class GameSet:
    def __init__(self, name, folder_path):
        self.name = name
        self.connection = sqlite3.connect(f"{name}.db")
        self.cursor = self.connection.cursor()

        self.load_games(folder_path)

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

    def load_games(self, folder_path):
        pass

    def add_game(self, game_path):
        with open(game_path, "r") as game_file:
            print(game_file.read())