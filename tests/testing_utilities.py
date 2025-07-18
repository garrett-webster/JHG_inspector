import json
import shutil

import pytest

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.logic_layer.DatabaseManager import DatabaseManager
from src.JHG_inspector.logic_layer.ToolsManager import ToolsManager


@pytest.fixture
def temp_folder(tmp_path):
    test_folder = tmp_path / "test_games"
    test_folder.mkdir()
    yield test_folder

@pytest.fixture
def database_manager(temp_folder):
    # Make sure JHGInspector creates a new DB at temp_folder
    return DatabaseManager(ToolsManager(), temp_folder / "test.db")

@pytest.fixture
def game_set(temp_folder, database_manager):
    def create_gameset(path=None, name = "test_set"):
        database_manager.games.load_games()
        gameset = database_manager.gamesets.create_gameset(name)
        if path is not None:
            if path.exists():
                for item in path.iterdir():
                    if item.is_file():
                        shutil.copy(item, temp_folder / item.name)

            database_manager.games.load_games_from_directory(path)
            for game_id in database_manager.games.all.keys():
                gameset.add_game(game_id)
        return gameset
    yield create_gameset
    database_manager.close()

@pytest.fixture
def game(temp_folder, game_set):
    def _create_game(path=None):

        # Use default if no data given
        if path is None:
            game = Game(game_set().database)
        else:
            with open(path, "r") as f:
                game_data = json.load(f)

            json_path = temp_folder / f"jhg_{game_data['lobby']['code']}.json"
            with open(json_path, "w") as f:
                json.dump(game_data, f)

            game = Game(game_set().database)
            game.load_from_file(json_path)
        return game
    return _create_game

@pytest.fixture
def cursor(temp_folder, database_manager):
    yield database_manager.connection.cursor()



