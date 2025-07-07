from pathlib import PosixPath

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.logic_layer.Gameset import Gameset

class GamesManager:
    """Used by the DatabaseManager to handle operations dealing with the games.

       The DatabaseManager has a reference to the GamesManager. Anytime that a change needs to be made to the games
       (loading, creation, deletion, etc), the request will be routed through the GamesManager, which then will access
       the Data Access Objects (DOAs) from the DatabaseManager to perform the database operations.
       """

    def __init__(self, database: "DatabaseManager"):
        self.database = database
        self.games = {}

        self.load_games()

    def __getitem__(self, game_id):
        return self.games[game_id]

    @property
    def all(self):
        """The preferred way to access self.games"""
        return self.games

    def load_games(self):
        """Loads all games from the database into the GamesManager object."""

        self.games = {}
        game_ids = self.database.DAOs["games"].select_all(["id"])

        for game_id in game_ids:
            game = Game(self.database)
            game.load_from_database(game_id[0])
            self.games[game_id[0]] = game

    def load_game_from_file(self, game_path: PosixPath):
        """Loads a single game from a passed file path."""

        new_game = Game(self.database)
        new_game.load_from_file(game_path)
        self.games[new_game.id] = new_game

        return new_game

    #TODO: Make it so it only tries to load game log files. Other files being present will brick the program.
    def load_games_from_directory(self, folder_path, gameset: Gameset = None):
        """Loads all game log files in a single directory"""
        game_paths = [f for f in folder_path.iterdir() if f.is_file()]
        new_games = []

        for game_path in game_paths:
            new_games.append(self.load_game_from_file(game_path))
        self.database.connection.commit()

        if gameset:
            for game in new_games:
                self.games[game.id] = game
                gameset.add_game(game.id)