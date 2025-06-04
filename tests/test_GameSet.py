import shutil
from pathlib import Path
from testing_utilities import *


class TestGameSetInitialization:
    def test_init(self, game_set):
        assert game_set.name == "test_set"

        cursor = game_set.connection.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
        expected_tables = ["searchTags", "gamesets", "games", "admins", "playersThatWillBeGovernment", "colorGroups",
            "labelPools", "customParams", "governmentRoundInfo", "players", "customRoundInfo", "transactions", "playerRoundInfo",
            "influences", "popularities", "groups", "groups_players", "chatInfo", "chatParticipants",
            "messages", "messageTargets", "gameset_games", "games_searchTags"]
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



