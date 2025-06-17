from pathlib import Path, PosixPath

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
    # from src.JHG_inspector.logic_layer.DatabaseAccess import DatabaseAccess
    def __init__(self, gameset_id, database_access):
        self.id = gameset_id
        self.database_access = database_access
        self.connection = database_access.connection
        self.update_signal = database_access.send_gameset_update

        self.games = {}
        self.cursor = self.connection.cursor()

        self.cursor.execute("SELECT name FROM gamesets WHERE id = ?", (self.id,))
        self.name = self.cursor.fetchone()[0]

    @update_function
    def load_games(self, base_path=None):
        self.cursor.execute("""SELECT games.id FROM games
                               JOIN gameset_games ON games.id = gameset_games.gameId
                               WHERE gameset_games.gamesetId = ?;""", (self.id,))
        game_ids = self.cursor.fetchall()
        for game_id in game_ids:
            self.add_game(game_id[0], base_path=base_path)

    @update_function
    def add_game(self, game_id: int, base_path=None):
        # new_game = Game(self.connection, base_path)
        # new_game.load_from_database(game_id)
        game = self.database_access.games[game_id]
        self.games[game.id] = game

        self.cursor.execute("SELECT gameId FROM gameset_games WHERE gamesetId = ? AND gameId = ?", (self.id, game_id))
        if self.cursor.fetchone() is None:
            self.cursor.execute("INSERT INTO gameset_games (gamesetId, gameId) VALUES (?, ?)", (self.id, game.id))
            self.connection.commit()

    def remove_game(self, game_id: int):
        self.cursor.execute("DELETE FROM gameset_games WHERE gamesetId = ? AND gameId = ?", (self.id, game_id))
        self.connection.commit()
        print(f"Removing game with id {game_id}...")