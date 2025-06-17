from pathlib import Path, PosixPath
from typing import Optional, Callable

from src.JHG_inspector.data_layer.Game import Game


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
    def __init__(self, gameset_id, connection, update_signal: Optional[Callable] = None):
        self.id = gameset_id
        self.connection = connection
        self.update_signal = update_signal

        self.games = {}
        self.cursor = connection.cursor()

        self.cursor.execute("SELECT name FROM gamesets WHERE id = ?", (self.id,))
        self.name = self.cursor.fetchone()[0]


    @update_function
    def load_games_from_folder(self, folder_path, base_path=None):
        game_paths = [f for f in Path(folder_path).iterdir() if f.is_file()]

        for game_path in game_paths:
            self.add_game_from_file(game_path, base_path=base_path)

        self.connection.commit()

    @update_function
    def load_games_from_database(self, base_path=None):
        self.cursor.execute("""SELECT games.id FROM games
                               JOIN gameset_games ON games.id = gameset_games.gameId
                               WHERE gameset_games.gamesetId = ?;""", (self.id,))
        game_ids = self.cursor.fetchall()
        for game_id in game_ids:
            self.add_game_from_database(game_id[0], base_path=base_path)

    @update_function
    def add_game_from_file(self, game_path: PosixPath, base_path=None):
        new_game = Game(self.connection, base_path)
        new_game.load_from_file(game_path)
        self.games[new_game.id] = new_game

        self.cursor.execute("INSERT INTO gameset_games (gamesetId, gameId) VALUES (?, ?)", (self.id, new_game.id))

    @update_function
    def add_game_from_database(self, game_id: int, base_path=None):
        new_game = Game(self.connection, base_path)
        new_game.load_from_database(game_id)
        self.games[new_game.id] = new_game

        self.cursor.execute("SELECT gameId FROM gameset_games WHERE gamesetId = ? AND gameId = ?", (self.id, game_id))
        if self.cursor.fetchone() is None:
            self.cursor.execute("INSERT INTO gameset_games (gamesetId, gameId) VALUES (?, ?)", (self.id, new_game.id))