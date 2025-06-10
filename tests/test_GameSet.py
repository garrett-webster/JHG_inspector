from pathlib import Path

from testing_utilities import *

FILE_PATH = Path(__file__).resolve().parent

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


    @pytest.mark.parametrize(
        "folder_name, expected_codes",
        [
            ("test_set0", set()),
            ("test_set1", {"GDHP", "MGNP", "PBSG"}),
        ]
    )
    def test_load_games_codes(self, game_set, folder_name, expected_codes, temp_folder):
        # Clear previous games from game_set to isolate runs
        test_gameset = game_set(FILE_PATH / folder_name)

        actual_codes = {game.code for game in test_gameset.games.values()}

        assert len(test_gameset.games) == len(expected_codes)
        assert actual_codes == expected_codes


    def test_load_games_gameset_games(self, game_set, temp_folder):
        test_gameset1 = game_set(FILE_PATH / "test_set1")
        test_gameset2 = game_set(FILE_PATH / "test_set2")

        test_gameset1.cursor.execute("SELECT * FROM gameset_games WHERE gamesetId = ?", (test_gameset1.id,))
        result = test_gameset1.cursor.fetchall()
        expected_results = [(1, 1), (1,2), (1,3)]
        assert result == expected_results

        test_gameset2.cursor.execute("SELECT * FROM gameset_games WHERE gamesetId = ?", (test_gameset2.id,))
        result = test_gameset2.cursor.fetchall()
        expected_results = [(2, 4), (2,5)]
        assert result == expected_results