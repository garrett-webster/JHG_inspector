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

    def test_init_database(self, game_loader):
        game, base_path = game_loader()

        db_path = base_path / "data_bases" / f"jhg_TEST.db"
        assert db_path.exists(), "Database file was not created"

        # Check expected tables exist
        game.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row[0] for row in game.cursor.fetchall()}
        game.connection.close()

        expected_tables = {
            "lobby", "miscData", "gameParams", "endCondition", "rounds", "players",
            "transactions", "playerRoundInfo", "popularities", "influences"
        }
        assert expected_tables == tables, f"Expected tables {expected_tables}, but found {tables}"

    def test_load_data_to_database_players(self, game_loader):
        game, base_path = game_loader(FILE_PATH / "test_set1/jhg_GDHP.json")
        game.load_data_to_database()

        # Fetch all players data from the database
        game.cursor.execute("""
            SELECT name, experience, permissionLevel, color, hue, avatar, icon
            FROM players
        """)
        players_in_db = game.cursor.fetchall()

        # Expected data
        expected_players = [
            ("Jane Doe", "beginner", "regular", None, None, None, None),
            ("James Doe", "beginner", "regular", None, None, None, None),
            ("John Doe", "beginner", "regular", None, None, None, None),
            ("Jessica Doe", "beginner", "regular", None, None, None, None),
        ]

        # Assert the count matches
        assert len(players_in_db) == len(expected_players), (
            f"Expected {len(expected_players)} players, found {len(players_in_db)}"
        )

        # Use Counter for unordered comparison with duplicates support
        assert players_in_db == expected_players, f"Expected players {expected_players}, but found {players_in_db}"

    def test_load_data_to_database_game_params_full(self, game_loader):
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