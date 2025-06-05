from pathlib import Path
from testing_utilities import *

FILE_PATH = Path(__file__).resolve().parent

class TestGameInitialization:
    def test_init_valid_path(self, game):
        test_game = game(FILE_PATH / "test_set1/jhg_GDHP.json")
        assert test_game.code == "GDHP"

    def test_init_invalid_path(self, game_set, temp_folder):
        with pytest.raises(FileNotFoundError):
            Game(game_set().connection, Path("test_set1/jhg_AAAA.json") , temp_folder)

    def test_load_data_to_database_games(self, game, temp_folder):
        test_game = game(FILE_PATH / "test_set1/jhg_GDHP.json")

        test_game.cursor.execute("SELECT * FROM games")
        actual_game_data = test_game.cursor.fetchone()

        expected_game_data = (1, "GDHP", 4, 0, "started", "2025-05-15T16:04:55.960738Z", 150000000, "radio", "none",
                              "freeForm", None, 10, 30, "time", 0.2, 0.5, 1.3, 0.95, 1.6, 0, 60, "ratio", True, 200, 50,
                              True, False, 1747325756118000, "time")

        assert actual_game_data == expected_game_data

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

    def test_load_data_to_database_influences(self, game, temp_folder):
        def extract_expected_influences(json_data, name_to_id, game_id):
            results = set()
            for round_name, round_data in json_data["influences"].items():
                round_num = int(round_name.split("_")[1])
                for sender, receivers in round_data.items():
                    sender_id = name_to_id[sender]
                    for receiver, amount in receivers.items():
                        if receiver != "__intrinsic__":
                            receiver_id = name_to_id[receiver]
                            results.add((game_id, round_num, sender_id, receiver_id, amount))
            return results

        test_game = game(FILE_PATH / "test_set2/jhg_GDSR.json")
        with open(FILE_PATH / "test_set2/jhg_GDSR.json") as f:
            data = json.load(f)

        expected_influences = extract_expected_influences(data, test_game.name_to_id, game_id=1)

        test_game.cursor.execute("SELECT * FROM influences")
        actual_influences = test_game.cursor.fetchall()

        assert expected_influences.issubset(set(actual_influences))

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