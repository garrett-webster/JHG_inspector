import json
import shutil
from pathlib import Path

import pytest

from src.JHG_inspector.Game import Game
from src.JHG_inspector.GameSet import GameSet
from src.JHG_inspector.JHGInspector import JHGInspector

@pytest.fixture
def temp_folder(tmp_path):
    test_folder = tmp_path / "test_games"
    test_folder.mkdir()
    yield test_folder

@pytest.fixture
def jhg_inspector(temp_folder):
    # Make sure JHGInspector creates a new DB at temp_folder
    return JHGInspector(temp_folder / "test.db")

@pytest.fixture
def game_set(temp_folder, jhg_inspector):
    def create_gameset(path=None, name = "test_set"):
        gameset = GameSet(name, jhg_inspector.connection, base_path=temp_folder)

        if path is not None:
            if path.exists():
                for item in path.iterdir():
                    if item.is_file():
                        shutil.copy(item, temp_folder / item.name)

            gameset.load_games(path)

        return gameset
    yield create_gameset
    jhg_inspector.close()

@pytest.fixture
def game(temp_folder, game_set):
    def _create_game(path=None):
        # Use default if no data given
        game_code = "TEST"
        if path:
            with open(path, "r") as f:
                game_data = json.load(f)
        else:
            game_data = {
                "players": [],
                "lobby": {
                    "code": game_code,
                    "gamesetId": game_set.id
                }
            }

        json_path = temp_folder / f"jhg_{game_data['lobby']['code']}.json"
        with open(json_path, "w") as f:
            json.dump(game_data, f)

        game = Game(game_set().connection, json_path, base_path=temp_folder)
        return game

    return _create_game



