from pathlib import Path

from tests.testing_utilities import *

TEST_DATA_PATH = Path(__file__).resolve().parent.parent / 'test_data'


class TestGameInitialization:
    def test_init_valid_path(self, game):
        test_game = game(TEST_DATA_PATH / "test_set1/jhg_GDHP.json")
        assert test_game.code == "GDHP"

    def test_init_invalid_path(self, game_set, temp_folder):
        with pytest.raises(FileNotFoundError):
            Game(game_set().database).load_from_file(TEST_DATA_PATH / "/test_set1/jhg_AAAA.json")

    def test_set_id_to_name_dicts(self, game):
        test_game1 = game(TEST_DATA_PATH / "test_set1/jhg_GDHP.json")
        test_game2 = game(TEST_DATA_PATH / "test_set1/jhg_MGNP.json")

        expected_game_1 = {1: "Bravo", 2: "Uniform", 3: "X-ray", 4: "Quebec"}
        expected_game_2 = {5: "Sierra", 6: "Romeo", 7: "Uniform", 8: "Tango"}

        assert test_game1.id_to_name == expected_game_1
        assert test_game2.id_to_name == expected_game_2

    def test_load_from_file(self, game):
        test_game1 = game(TEST_DATA_PATH / "test_set1/jhg_GDHP.json")
        test_game2 = game(TEST_DATA_PATH / "test_set1/jhg_MGNP.json")
        test_game3 = game(TEST_DATA_PATH / "test_set1/jhg_GDHP.json")

        assert test_game1.id == 1
        assert test_game2.id == 2
        assert test_game3.id == 1

        assert test_game1.code == "GDHP"
        assert test_game2.code == "MGNP"
        assert test_game3.code == "GDHP"

    def test_load_from_database(self, game, game_set):
        game(TEST_DATA_PATH / "test_set1/jhg_GDHP.json")

        test_game = game()
        test_game.load_from_database(1)

        assert test_game.id == 1
        assert test_game.code == "GDHP"


class TestGameProperties:
    @pytest.mark.parametrize("game_path,expected", [
        ("test_set1/jhg_GDHP.json", [
            [100, 100, 100, 100],
            [101.625, 101.625, 101.625, 101.625]
        ]),
        ("test_set2/jhg_GDSR.json", [
            [100, 100, 100, 100],
            [102.95833333333334, 97.16666666666667, 84.0, 98.375],
            [101.28556561170396, 100.11781560231618, 81.9074674379407, 83.80281454248367],
            [87.10909848681052, 99.02186957374734, 85.49486724848725, 81.02336101116774]
        ])
    ])
    def test_popularities(self, game_path, expected, game):
        test_game = game(TEST_DATA_PATH / game_path)

        assert test_game.popularities == expected

    @pytest.mark.parametrize("game_path,expected", [
        ("test_set1/jhg_GDHP.json", [
            [[0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]],
            [[11.875, 3.25, 3.25, 3.25],
             [3.25, 11.875, 3.25, 3.25],
             [3.25, 3.25, 11.875, 3.25],
             [3.25, 3.25, 3.25, 11.875]]
        ]),
        ("test_set2/jhg_GDSR.json", [
            [[0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]],
             [[13.208333333333336, 0, 6.5, 3.25],
              [0, 7.416666666666668, 6.5, 3.25],
              [-1.3333333333333337, -2.6666666666666674, 4.75, 3.25],
              [0, 0, 6.5, 11.875]],
             [[23.369883422161465, 0, 4.883921568627452, 9.031760620915033],
              [3.3461458333333343, 18.85598757944035, 4.883921568627452, 9.031760620915033],
              [2.0668346470106513, -2.4840003605182766, 9.29287253053327,9.031760620915033],
              [3.3461458333333343,-1.002813743976535, 3.150068645937319,14.309413807189543]],
             [[23.77908947731485, 3.253829007075276, 3.3199078491867695, 5.556272153233606],
              [9.293918029164665, 27.77409293018228, 3.9362919264672573, 6.817566687933123],
              [8.222752431962562, 1.1244557308394518, 18.13009239775211, 6.817566687933123],
              [9.293918029164665, 2.2465417547917736, 2.2430829229676448, 16.039818304243635]]
        ])
    ])
    def test_influences(self, game_path, expected, game):
        test_game = game(TEST_DATA_PATH / game_path)

        assert test_game.influences == expected

    @pytest.mark.parametrize("game_path,expected", [
        ("test_set1/jhg_GDHP.json", [
            [[5, 1, 1, 1], [1, 5, 1, 1], [1, 1, 5, 1], [1, 1, 1, 5]]
        ]),
        ("test_set2/jhg_GDSR.json", [
            [[5, -1, -1, -1], [-2, 2, -2, -2], [2, 2, 2, 2], [1, 1, 1, 5]],
            [[5, 1, 1, 1], [-1, 5, -1, -1], [-2, -2, 2, -2], [2, 2, 2, 2]],
            [[2, 2, 2, 2], [1, 5, 1, 1], [-1, -1, 5, -1], [-2, -2, -2, 2]]
        ])
    ])
    def test_transactions(self, game_path, expected, game):
        test_game = game(TEST_DATA_PATH / game_path)

        assert test_game.transactions == expected

    @pytest.mark.parametrize("game_path,expected", [
        ("test_set1/jhg_GDHP.json", ["none", "freeForm", None, 10, 30, "time", 0, 60, "ratio", False, 200, 50, True, False, 1747325756118000, "time"]),
    ],)
    def test_settings(self, game_path, expected, game):
        test_game = game(TEST_DATA_PATH / game_path)
        columns = ["chatType", "messageType", "advancedGameSetup", "gameEndLow", "gameEndHigh", "gameEndType",
                   "povertyLine",
                   "govInitialPopularity", "govInitialPopularityType", "govRandomPopularities", "govRandomPopHigh",
                   "govRandomPopLow", "govSendVotesImmediately", "labelsEnabled", "duration", "runtimeType"]

        for i, column in enumerate(columns):
            assert test_game.settings[column] == expected[i]

    @pytest.mark.parametrize("game_path,expected", [
        ("test_set1/jhg_GDHP.json", [0.2, 0.5, 1.3, 0.95, 1.6, 150000000]),
        ("test_set2/jhg_GDSR.json", [0.2, 0.5, 1.3, 0.95, 1.6, 150000000])
    ])
    def test_parameters(self, game_path, expected, game):
        test_game = game(TEST_DATA_PATH / game_path)
        columns = ["alpha", "beta", "cGive", "cKeep", "cSteal", "lengthOfRound"]

        for i, column in enumerate(columns):
            assert test_game.parameters[column] == expected[i]