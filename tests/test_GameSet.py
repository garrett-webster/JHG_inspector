import json

import pytest
from src.JHG_inspector.GameSet import GameSet
import shutil
from pathlib import Path


@pytest.fixture
def game_set(temp_folder):
    return GameSet("test_set", base_path=temp_folder)


@pytest.fixture
def temp_folder(tmp_path):
    test_folder = tmp_path / "test_games"
    test_folder.mkdir()
    yield test_folder


class TestGameSetInitialization:
    def test_init(self, game_set):
        assert game_set.name == "test_set"

        cursor = game_set.connection.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        expected_tables = ["games", "players"]
        actual_tables = [row[0] for row in cursor.fetchall()]

        assert actual_tables == expected_tables


    @pytest.mark.parametrize(
        "folder_name, expected_codes",
        [
            ("test_set0", set()),
            ("test_set1", {"GDHP", "MGNP", "PBSG"}),
        ]
    )
    def test_load_games(self, game_set, folder_name, expected_codes, temp_folder):
        # Clear previous games from game_set to isolate runs
        game_set.games.clear()

        # Create a copy of the sample data to test on
        source_dir = Path(__file__).parent / folder_name
        if source_dir.exists():
            for item in source_dir.iterdir():
                if item.is_file():
                    shutil.copy(item, temp_folder / item.name)

        # Load games with temp_folder as base_path (DB files will go here)
        game_set.load_games(str(temp_folder), base_path=temp_folder)

        actual_codes = {game.code for game in game_set.games.values()}

        assert len(game_set.games) == len(expected_codes)
        assert actual_codes == expected_codes

        # Assert database files were created for each expected game code
        db_dir = temp_folder / "data_bases"
        db_file = db_dir / f"gameset_test_set.db"
        assert db_file.exists(), f"DB file missing"

    def test_schema_columns_match_json(self, game_set):
        # Load schema from JSON
        schema_path = Path(__file__).parent.parent / "src" / "JHG_inspector" / "DB_commands" / "schema.json"
        with open(schema_path, "r") as f:
            expected_schema = json.load(f)

        cursor = game_set.connection.cursor()

        for table, expected_columns in expected_schema.items():
            cursor.execute(f"PRAGMA table_info({table})")
            actual_columns = [row[1] for row in cursor.fetchall()]  # row[1] = column name

            expected_column_names = list(expected_columns.keys())

            assert actual_columns == expected_column_names, (
                f"Mismatch in columns for table '{table}':\n"
                f"Expected: {expected_column_names}\n"
                f"Actual:   {actual_columns}"
            )