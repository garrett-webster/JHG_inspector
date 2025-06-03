import json

from pathlib import Path
from src.JHG_inspector.Game import Game
from testing_utilities import *

FILE_PATH = Path(__file__).resolve().parent

class TestGameInitialization:
    def test_init_valid_path(self, game):
        assert game().code == "TEST"

    def test_init_invalid_path(self, game_set, temp_folder):
        with pytest.raises(FileNotFoundError):
            Game(game_set.connection, Path("test_set1/jhg_AAAA.json") , temp_folder)

    # Tests that the players table is correctly loaded into the database
    def test_load_data_to_database_players(self, game, temp_folder):
        test_game = game(FILE_PATH / "test_set1/jhg_GDHP.json")

        # Fetch all players data from the database
        test_game.cursor.execute("""
            SELECT id, name, experience, permissionLevel, color, hue, avatar, icon
            FROM players
        """)
        players_in_db = test_game.cursor.fetchall()

        # Expected data
        expected_players = [
            (1, "Jane Doe", "beginner", "regular", None, None, None, None),
            (2, "James Doe", "beginner", "regular", None, None, None, None),
            (3, "John Doe", "beginner", "regular", None, None, None, None),
            (4, "Jessica Doe", "beginner", "regular", None, None, None, None),
        ]

        # Assert the count matches
        assert len(players_in_db) == len(expected_players), (
            f"Expected {len(expected_players)} players, found {len(players_in_db)}"
        )

        # Use Counter for unordered comparison with duplicates support
        assert players_in_db == expected_players, f"Expected players {expected_players}, but found {players_in_db}"

    def test_set_id_to_name_dictionary(self, game):
        test_game1 = game(FILE_PATH / "test_set1/jhg_GDHP.json")
        test_game3 = game(FILE_PATH / "test_set1/jhg_GDHP.json")
