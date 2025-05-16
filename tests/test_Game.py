import json
import sqlite3
import pytest
from pathlib import Path
from src.JHG_inspector.Game import Game


@pytest.fixture
def prepared_game(tmp_path):
    # Setup temp test environment
    game_code = "TEST"
    json_path = tmp_path / f"jhg_{game_code}.json"
    db_dir = tmp_path / "data_bases"
    db_dir.mkdir()

    # Create minimal valid JSON file
    sample_data = {
        "players": [],
        "lobby": {
            "code": game_code
        }
    }
    with open(json_path, "w") as f:
        json.dump(sample_data, f)
    return Game(json_path, base_path=tmp_path), tmp_path


class TestGameInitialization:
    def test_init_valid_path(self, prepared_game):
        game, _ = prepared_game
        assert game.code == "TEST"

    def test_init_invalid_path(self):
        with pytest.raises(FileNotFoundError):
            Game(Path("test_set1/jhg_AAAA.json"))

    def test_init_database(self, prepared_game):
        game, base_path = prepared_game

        db_path = base_path / "data_bases" / f"jhg_TEST.db"
        assert db_path.exists(), "Database file was not created"

        # Check expected tables exist
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()

        expected_tables = {
            "miscSettings", "gameParams", "popularityFunctionParams",
            "governmentParams", "endCondition", "rounds", "players",
            "transactions", "playerRoundInfo", "popularities", "influences"
        }
        assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"