from pathlib import Path

from src.JHG_inspector.Game import Game


class GameSet:
    def __init__(self, name):
        self.games = {}
        self.name = name

    def load_games(self, folder_path, base_path=None):
        game_paths = [f for f in Path(folder_path).iterdir() if f.is_file()]

        for game_path in game_paths:
            # TODO: Add a try catch here to catch if the file is not found.
            self.add_game(Game(game_path, base_path))

    def add_game(self, game: Game):
        self.games[game.code] = game