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

    def test_load_games_from_database(self, database_access):
        database_access.load_games_from_folder(Path(FILE_PATH.parent / "test_set1"))
        test_gameset = database_access.create_gameset("testing")
        for game_id in database_access.games.keys():
            test_gameset.add_game(game_id)

        loaded_games = list(test_gameset.games.values())

        test_gameset.games.clear()
        test_gameset.load_games()

        assert len(test_gameset.games) == len(loaded_games)
        for i, game in enumerate(test_gameset.games.values()):
            assert game.code == loaded_games[i].code
            assert game.id == loaded_games[i].id

    def test_add_game_from_database(self, game, game_set):
        game(FILE_PATH.parent / "test_set2/jhg_GDSR.json")
        test_gameset = game_set(FILE_PATH.parent / "test_set1")
        test_gameset.add_game(1)

        expected_game_codes = ["GDSR", "MGNP", "GDHP", "PBSG"]
        expected_game_ids = [1, 2, 3, 4]

        for i, game in enumerate(test_gameset.games.values()):
            assert game.code == expected_game_codes[i]
            assert game.id == expected_game_ids[i]