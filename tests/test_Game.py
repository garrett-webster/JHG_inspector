import json

from pathlib import Path
from src.JHG_inspector.Game import Game
from testing_utilities import *

FILE_PATH = Path(__file__).resolve().parent

class TestGameInitialization:
    def test_init_valid_path(self, game):
        test_game = game(FILE_PATH / "test_set1/jhg_GDHP.json")
        assert test_game.code == "GDHP"

    def test_init_invalid_path(self, game_set, temp_folder):
        with pytest.raises(FileNotFoundError):
            Game(game_set.connection, Path("test_set1/jhg_AAAA.json") , temp_folder)

    # Tests that the players table is correctly loaded into the database
    def test_load_data_to_database_players(self, game, temp_folder):
        test_game = game(FILE_PATH / "test_set1/jhg_GDHP.json")

        # Fetch all players data from the database
        test_game.cursor.execute("""
            SELECT id, name, experience, permissionLevel, color, hue, avatar, icon
            FROM players
        """)
        players_in_db = test_game.cursor.fetchall()

        # Expected data
        expected_players = [
            (1, "Jane Doe", "beginner", "regular", None, None, None, None),
            (2, "James Doe", "beginner", "regular", None, None, None, None),
            (3, "John Doe", "beginner", "regular", None, None, None, None),
            (4, "Jessica Doe", "beginner", "regular", None, None, None, None),
        ]

        # Assert the count matches
        assert len(players_in_db) == len(expected_players), (
            f"Expected {len(expected_players)} players, found {len(players_in_db)}"
        )

        # Use Counter for unordered comparison with duplicates support
        assert players_in_db == expected_players, f"Expected players {expected_players}, but found {players_in_db}"

    def test_load_data_to_database_transactions(self, game, temp_folder):
        def extract_expected_transactions(json_data, name_to_id, game_id):
            results = set()
            for round_name, round_data in json_data["transactions"].items():
                round_num = int(round_name.split("_")[1])
                for sender, receivers in round_data.items():
                    sender_id = name_to_id[sender]
                    for receiver, amount in receivers.items():
                        receiver_id = name_to_id[receiver]
                        results.add((game_id, round_num, sender_id, receiver_id, amount))
            return results

        test_game = game(FILE_PATH / "test_set2/jhg_GDSR.json")
        with open(FILE_PATH / "test_set2/jhg_GDSR.json") as f:
            data = json.load(f)

        expected_transactions = extract_expected_transactions(data, test_game.name_to_id, game_id=1)

        test_game.cursor.execute("SELECT * FROM transactions")
        actual_transactions = test_game.cursor.fetchall()

        assert expected_transactions.issubset(set(actual_transactions))

    def test_load_data_to_database_popularities(self, game):
        def extract_expected_popularities(json_data, name_to_id, game_id):
            results = set()
            for round_index, (round_name, round_data) in enumerate(json_data["popularities"].items()):
                round_num = round_index + 1
                for name, score in round_data.items():
                    results.add((game_id, round_num, name_to_id[name], score))
            return results

        test_game = game(FILE_PATH / "test_set2/jhg_GDSR.json")
        with open(FILE_PATH / "test_set2/jhg_GDSR.json") as f:
            json_data = json.load(f)

        expected = extract_expected_popularities(json_data, test_game.name_to_id, game_id=1)

        test_game.cursor.execute("SELECT * FROM popularities")
        actual = set(test_game.cursor.fetchall())

        # For floats, compare with tolerance
        for ex in expected:
            assert any(
                ex[:3] == ac[:3] and abs(ex[3] - ac[3]) < 1e-6
                for ac in actual
            ), f"Expected popularity {ex} not found"

    def test_set_id_to_name_dicts(self, game):
        test_game1 = game(FILE_PATH / "test_set1/jhg_GDHP.json")
        test_game2 = game(FILE_PATH / "test_set1/jhg_MGNP.json")
        test_game3 = game(FILE_PATH / "test_set1/jhg_GDHP.json")

        expected_game_1 = {1: "Bravo", 2: "Uniform", 3: "X-ray", 4 : "Quebec"}
        expected_game_2 = {5: "Sierra", 6: "Romeo", 7: "Uniform", 8: "Tango"}

        assert test_game1.id_to_name == test_game3.id_to_name
        assert test_game1.id_to_name == expected_game_1
        assert test_game3.id_to_name == expected_game_1
        assert test_game2.id_to_name == expected_game_2