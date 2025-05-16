import pytest
from src.JHG_inspector.GameSet import GameSet
import shutil
from pathlib import Path


@pytest.fixture
def game_set():
    return GameSet("test set")


@pytest.fixture
def temp_folder(tmp_path):
    test_folder = tmp_path / "test_games"
    test_folder.mkdir()
    yield test_folder


class TestGameSetInitialization:
    def test_init(self, game_set):
        assert game_set.name == "test set"

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
        for code in expected_codes:
            db_file = db_dir / f"jhg_{code}.db"
            assert db_file.exists(), f"DB file missing for {code}"

        # Check no unexpected DB files remain
        db_files = set(p.name for p in db_dir.glob("*.db")) if db_dir.exists() else set()
        expected_db_files = {f"jhg_{code}.db" for code in expected_codes}
        assert db_files == expected_db_files