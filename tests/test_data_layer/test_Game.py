from pathlib import Path

from src.JHG_inspector.data_layer.Game import AlreadyExistsError
from tests.testing_utilities import *

FILE_PATH = Path(__file__).resolve().parent


class TestGameInitialization:
    def test_init_valid_path(self, game):
        test_game = game(FILE_PATH.parent / "test_set1/jhg_GDHP.json")
        assert test_game.code == "GDHP"

    def test_init_invalid_path(self, game_set, temp_folder):
        with pytest.raises(FileNotFoundError):
            Game(game_set().connection, temp_folder).load_from_file(Path("test_set1/jhg_AAAA.json"))

    def test_set_id_to_name_dicts(self, game):
        test_game1 = game(FILE_PATH.parent / "test_set1/jhg_GDHP.json")
        test_game2 = game(FILE_PATH.parent / "test_set1/jhg_MGNP.json")

        expected_game_1 = {1: "Bravo", 2: "Uniform", 3: "X-ray", 4: "Quebec"}
        expected_game_2 = {5: "Sierra", 6: "Romeo", 7: "Uniform", 8: "Tango"}

        assert test_game1.id_to_name == expected_game_1
        assert test_game2.id_to_name == expected_game_2

    def test_load_from_file(self, game):
        test_game1 = game(FILE_PATH.parent / "test_set1/jhg_GDHP.json")
        test_game2 = game(FILE_PATH.parent / "test_set1/jhg_MGNP.json")
        with pytest.raises(AlreadyExistsError):
            game(FILE_PATH.parent / "test_set1/jhg_GDHP.json")

        assert test_game1.id == 1
        assert test_game2.id == 2

        assert test_game1.code == "GDHP"
        assert test_game2.code == "MGNP"

    def test_load_from_database(self, game, game_set):
        game(FILE_PATH.parent / "test_set1/jhg_GDHP.json")

        test_game = game()
        test_game.load_from_database(1)

        assert test_game.id == 1
        assert test_game.code == "GDHP"