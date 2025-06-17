from pathlib import Path

from tests.test_data_layer.data_layer_testing_utilities import *

FILE_PATH = Path(__file__).resolve()

class TestGameSetInitialization:
    def test_init(self, game_set):
        assert game_set().name == "test_set"

        cursor = game_set().connection.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
        expected_tables = ["searchTags", "gamesets", "games", "players", "admins", "playersThatWillBeGovernment", "colorGroups",
            "labelPools", "customParams", "governmentRoundInfo", "customRoundInfo", "transactions", "playerRoundInfo",
            "influences", "popularities", "groups", "groups_players", "chatInfo", "chatParticipants",
            "messages", "messageTargets", "gameset_games"]
        actual_tables = [row[0] for row in cursor.fetchall()]

        assert actual_tables == expected_tables

    def test_load_games_from_folder_codes(self, game_set, temp_folder):
        # Clear previous games from game_set to isolate runs
        test_gameset = game_set(FILE_PATH.parent / "test_set1")

        actual_codes = {game.code for game in test_gameset.games.values()}
        expected_codes = {"GDHP", "MGNP", "PBSG"}

        assert len(test_gameset.games) == len(expected_codes)
        assert actual_codes == expected_codes


    def test_load_games_from_folder_gameset_games(self, game_set, temp_folder):
        test_gameset1 = game_set(FILE_PATH.parent / "test_set1")
        test_gameset2 = game_set(FILE_PATH.parent / "test_set2")

        test_gameset1.cursor.execute("SELECT * FROM gameset_games WHERE gamesetId = ?", (test_gameset1.id,))
        result = test_gameset1.cursor.fetchall()
        expected_results = [(1, 1), (1,2), (1,3)]
        assert result == expected_results

        test_gameset2.cursor.execute("SELECT * FROM gameset_games WHERE gamesetId = ?", (test_gameset2.id,))
        result = test_gameset2.cursor.fetchall()
        expected_results = [(2, 4), (2,5)]
        assert result == expected_results

    def test_load_games_from_database(self, database_access):
        test_gameset = database_access.create_gameset("testing")
        test_gameset.load_games_from_folder(str(Path(FILE_PATH / "../test_set1").resolve()), base_path=Path(FILE_PATH))

        loaded_games = list(test_gameset.games.values())

        test_gameset.games.clear()
        test_gameset.load_games_from_database()

        assert len(test_gameset.games) == len(loaded_games)
        for i, game in enumerate(test_gameset.games.values()):
            assert game.code == loaded_games[i].code
            assert game.id == loaded_games[i].id

    def test_add_game_from_file(self, game_set):
        test_gameset = game_set(FILE_PATH.parent / "test_set1")

        test_gameset.add_game_from_file(FILE_PATH.parent / "test_set2/jhg_GDSR.json")

        expected_game_codes = ["MGNP", "GDHP", "PBSG", "GDSR"]
        assert len(test_gameset.games) == len(expected_game_codes)
        for _, game in test_gameset.games.items():
            assert game.code in expected_game_codes

    def test_add_game_from_database(self, game, game_set):
        game(FILE_PATH.parent / "test_set2/jhg_GDSR.json")
        test_gameset = game_set(FILE_PATH.parent / "test_set1")
        test_gameset.add_game_from_database(1)

        expected_game_codes = ["MGNP", "GDHP", "PBSG", "GDSR"]
        expected_game_ids = [2, 3, 4, 1]

        for i, game in enumerate(test_gameset.games.values()):
            assert game.code == expected_game_codes[i]
            assert game.id == expected_game_ids[i]