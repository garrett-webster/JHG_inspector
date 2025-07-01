from pathlib import Path
from typing import Callable

FILE_PATH = Path(__file__).resolve().parent

# Decorated functions will automatically call the update_signals method
def update_function(func):
    def wrapper(*args, **kwargs):
        if args[0].update_signal is not None:
            self = args[0]
            func(*args, **kwargs)
            self.update_signal(self.id)
        else:
            func(*args, **kwargs)
    return wrapper

# I might want to add a permanent/temporary flag (or maybe visible/invisible) to allow for a tool to clone a gameset and add games temporarily without making it persistent
class Gameset:
    """Holds the data for a single gameset"""
    def __init__(self, gameset_id, database: "DatabaseManager", update_signal: Callable):
        self.id = gameset_id
        self.database = database
        self.update_signal = update_signal

        self.games = {}

        self.name = database.DAOs["gamesets"].select_one(["name"], ["id"], [self.id])[0]

    @update_function
    def load_games(self, base_path=None):
        """Find the gameset record in the database based on the games id and load the data from the database"""

        game_ids = self.database.DAOs["GamesGameset_gamesDao"].select_all(["games.id"], ["gameset_games.gamesetId"], [self.id])
        for game_id in game_ids:
            self.add_game(game_id[0], base_path=base_path)

    @update_function
    def add_game(self, game_id: int, base_path=None):
        """Find the game record in the database based on the games id and add it to self.games as well as creating a
           database record of the relationship in gameset_games
           """

        game = self.database.games[game_id]
        self.games[game.id] = game

        if self.database.DAOs["gameset_games"].select_one(["gameId"], ["gamesetId", "gameId"], [self.id, game_id]) is None:
            self.database.DAOs["gameset_games"].insert_one((self.id, game.id))
            self.database.connection.commit()

    def remove_game(self, game_id: int):
        """Remove the record in gameset_games that relates the game with passed id to the gameset represented by this
           object.
           """

        print(f"Removing game with id {game_id}...")

        self.database.DAOs["gameset_games"].delete_one(["gamesetId", "gameId"], (self.id, game_id))
        self.database.connection.commit()

        del self.games[game_id]