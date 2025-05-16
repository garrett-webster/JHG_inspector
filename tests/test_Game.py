import json
import shutil
import sqlite3
import pytest
from pathlib import Path
from src.JHG_inspector.Game import Game


def load_game_utility(tmp_path, game_path=None):
    # Setup temp test environment
    db_dir = tmp_path / "data_bases"
    db_dir.mkdir()

    if game_path is None:
        game_code = "TEST"
        json_path = tmp_path / f"jhg_{game_code}.json"

        # Create minimal valid JSON file
        sample_data = {
            "players": [],
            "lobby": {
                "code": game_code
            }
        }
        with open(json_path, "w") as f:
            json.dump(sample_data, f)
    else:
        with open(game_path, "r") as f:
            sample_data = json.load(f)

        json_path = tmp_path / f"jhg_{sample_data['lobby']['code']}.json"
        with open(json_path, "w") as f:
            json.dump(sample_data, f)

    return Game(json_path, base_path=tmp_path), tmp_path


class TestGameInitialization:
    def test_init_valid_path(self, tmp_path):
        game, _ = load_game_utility(tmp_path)
        assert game.code == "TEST"

    def test_init_invalid_path(self):
        with pytest.raises(FileNotFoundError):
            Game(Path("test_set1/jhg_AAAA.json"))

    def test_init_database(self, tmp_path):
        game, base_path = load_game_utility(tmp_path)

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

    # def test_load_data_to_database(self, prepared_game):