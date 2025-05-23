import json
import shutil
import sqlite3
from collections import Counter

import pytest
from pathlib import Path
from src.JHG_inspector.Game import Game

FILE_PATH = Path(__file__).resolve().parent


@pytest.fixture
def game_loader(tmp_path):
    def _load_game(game_path=None):
        db_dir = tmp_path / "data_bases"
        db_dir.mkdir()

        if game_path is None:
            game_code = "TEST"
            json_path = tmp_path / f"jhg_{game_code}.json"
            sample_data = {
                "players": [],
                "lobby": {"code": game_code}
            }
            json_path.write_text(json.dumps(sample_data))
        else:
            with open(game_path) as f:
                sample_data = json.load(f)
            code = sample_data["lobby"]["code"]
            json_path = tmp_path / f"jhg_{code}.json"
            json_path.write_text(json.dumps(sample_data))

        return Game(json_path, base_path=tmp_path), tmp_path
    return _load_game


class TestGameInitialization:
    def test_init_valid_path(self, game_loader):
        game, _ = game_loader()
        assert game.code == "TEST"

    def test_init_invalid_path(self):
        with pytest.raises(FileNotFoundError):
            Game(Path("test_set1/jhg_AAAA.json"))

    # Tests that the players table is correctly loaded into the database
    def test_load_data_to_database_players(self, game_loader):
        game, base_path = game_loader(FILE_PATH / "test_set1/jhg_GDHP.json")
        game.load_data_to_database()

        # Fetch all players data from the database
        game.cursor.execute("""
            SELECT id, name, experience, permissionLevel, color, hue, avatar, icon
            FROM players
        """)
        players_in_db = game.cursor.fetchall()

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

    # Tests that the gameParams table is correctly loaded into the database
    def test_load_data_to_database_game_params(self, game_loader):
        game, base_path = game_loader(FILE_PATH / "test_set1/jhg_GDHP.json")
        game.load_data_to_database()

        game.cursor.execute("SELECT * FROM gameParams")
        result = game.cursor.fetchone()

        expected = (
            150000000,  # lengthOfRound
            "radio",  # nameSet
            "none",  #chatType
            "freeForm",  #messageType

            10, 30, "time",  # gameEndCriteria

            0.2, 0.5, 1.3, 0.95, 1.6, 0.0, 1,  # popularityFunctionParams

            60.0, "ratio", 1, 200.0, 50.0, None, 1,  # governmentParams

            0,  # labels.enabled

            1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1,  # show.*

            1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1  # allowEdit.*
        )

        assert result == expected, f"Expected {expected}, but got {result}"

    def test_load_data_to_database_lobby(self, game_loader):
        game, base_path = game_loader(FILE_PATH / "test_set1/jhg_GDHP.json")
        game.load_data_to_database()

        game.cursor.execute("SELECT * FROM lobby")
        result = game.cursor.fetchone()

        expected = ("GDHP", 4, 0, None, 1)

        assert result == expected, f"Expected {expected}, but got {result}"

    def test_load_data_to_database_endCondition(self, game_loader):
        game, base_path = game_loader(FILE_PATH / "test_set1/jhg_GDHP.json")
        game.load_data_to_database()

        game.cursor.execute("SELECT * FROM endCondition")
        result = game.cursor.fetchone()

        expected = (1747325756118000, "time")

        assert result == expected, f"Expected {expected}, but got {result}"
