from pathlib import Path

from src.JHG_inspector.old_data_layer.game_file_loaders import GameFileLoader
from tests.test_old_data_layer.data_layer_testing_utilities import *

FILE_PATH = Path(__file__).resolve().parent

class TestGameFileLoader:
    def test_prepare_sql_strings(self, game):
        test_game = test_game = game(FILE_PATH.parent / "test_set1/jhg_GDHP.json")
        test_game_loader = GameFileLoader(test_game)
        columns, column_names, placeholders = test_game_loader._prepare_sql_strings("players")

        expected_columns = [('gameName', 'TEXT'), ('name', 'TEXT'), ('experience', 'TEXT'), ('permissionLevel', 'TEXT'),
                            ('color', 'TEXT'), ('hue', 'TEXT'), ('avatar', 'TEXT'), ('icon', 'TEXT')]
        expected_column_names = "gameId, gameName, name, experience, permissionLevel, color, hue, avatar, icon"
        expected_placeholders = "?, ?, ?, ?, ?, ?, ?, ?, ?"

        assert columns == expected_columns
        assert column_names == expected_column_names
        assert placeholders == expected_placeholders