from pathlib import Path

from tests.test_old_data_layer.data_layer_testing_utilities import *

FILE_PATH = Path(__file__).resolve().parent
TESTS_PATH = FILE_PATH.parent


class TestGameFileLoader_JsonV1:
    def test_load_data_to_database_games(self, game, temp_folder):
        test_game = game(TESTS_PATH / "test_set1/jhg_GDHP.json")

        test_game.cursor.execute("SELECT * FROM games")
        actual_game_data = test_game.cursor.fetchone()

        expected_game_data = (1, "GDHP", 4, 0, "finished", "2025-05-15T16:04:55.960738Z", 150000000, "radio", "none",
                              "freeForm", None, 10, 30, "time", 0.2, 0.5, 1.3, 0.95, 1.6, 0.0, 60, "ratio", 0, 200, 50,
                              1, 0, 1747325756118000, "time")

        assert actual_game_data == expected_game_data

    def test_load_searchTags_data(self, game):
        test_game = game(TESTS_PATH / "test_set1/jhg_GDHP.json")

        expected_search_tags = [
            ("show_roundLength",), ("show_gameLength",), ("show_chatType",), ("show_messageType",), ("show_nameSet",),
            ("show_initialSetup",), ("show_grouping",), ("show_labels",), ("show_advancedParams",),
            ("show_government",),
            ('show_popularityRandomization',), ("show_visibilities",), ("show_colorGrouping",), ("show_pregame",),
            ("show_agents",), ("allowEdit_roundLength",), ("allowEdit_gameLength",), ("allowEdit_chatType",),
            ("allowEdit_messageType",), ("allowEdit_nameSet",), ("allowEdit_initialSetup",), ("allowEdit_grouping",),
            ("allowEdit_labels",), ("allowEdit_advancedParams",), ("allowEdit_government",),
            ('allowEdit_popularityRandomization',), ("allowEdit_visibilities",), ("allowEdit_colorGrouping",),
            ("allowEdit_pregame",), ("allowEdit_agents",),
        ]
        test_game.cursor.execute("SELECT tag FROM searchTags")
        actual_search_tags = test_game.cursor.fetchall()

        assert actual_search_tags == expected_search_tags

        expected_search_tag_values = [("1",), ("1",), ("1",), ("1",), ("1",), ("1",), ("1",), ("1",), ("1",), ("1",),
                                      ("1",), ("1",), ("1",), ("1",), ("1",), ("1",), ("1",), ("1",), ("1",), ("1",),
                                      ("1",), ("1",), ("1",), ("1",), ("1",), ("1",), ("1",), ("1",), ("1",), ("1",)
                                      ]
        test_game.cursor.execute("SELECT value FROM searchTags")
        actual_search_tag_values = test_game.cursor.fetchall()

        assert actual_search_tag_values == expected_search_tag_values

    def test_load_playersThatWillBeGovernment_data(self, game, temp_folder):
        test_game = game(TESTS_PATH / "test_set3/jhg_NMBT.json")

        test_game.cursor.execute("SELECT playerId FROM playersThatWillBeGovernment")
        actual_players = test_game.cursor.fetchall()
        expected_players = [(9,), (1,)]

        assert actual_players == expected_players

    def test_load_colorGroups_data(self, game, temp_folder):
        test_game = game(TESTS_PATH / "test_set3/jhg_DGMT.json")

        test_game.cursor.execute("SELECT * FROM colorGroups")
        actual_color_groups = test_game.cursor.fetchall()
        expected_color_groups = [(1, 50, "Red"), (1, 25, "Blue")]

        assert expected_color_groups == actual_color_groups

    # Tests that the players table is correctly loaded into the database
    def test_load_data_to_database_players(self, game, temp_folder):
        test_game = game(TESTS_PATH / "test_set1/jhg_GDHP.json")

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

        test_game = game(TESTS_PATH / "test_set2/jhg_GDSR.json")
        with open(TESTS_PATH / "test_set2/jhg_GDSR.json") as f:
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

        test_game = game(TESTS_PATH / "test_set2/jhg_GDSR.json")
        with open(TESTS_PATH / "test_set2/jhg_GDSR.json") as f:
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

        test_game = game(TESTS_PATH / "test_set2/jhg_GDSR.json")
        with open(TESTS_PATH / "test_set2/jhg_GDSR.json") as f:
            data = json.load(f)

        expected_influences = extract_expected_influences(data, test_game.name_to_id, game_id=1)

        test_game.cursor.execute("SELECT * FROM influences")
        actual_influences = test_game.cursor.fetchall()

        assert expected_influences.issubset(set(actual_influences))

    def test_load_chatInfo_data(self, game):
        test_game = game(TESTS_PATH / "test_set2/jhg_XJPV.json")
        test_game.cursor.execute("SELECT * FROM chatInfo")
        actual_chats = test_game.cursor.fetchall()

        expected_chats = [
            (1, 1, "-OS4sOQs0a34MI3Pb8U4", "RAH"),
            (2, 1, "-OS4sOsEKJIlWUQBmx8A", "With Mike"),
            (3, 1, "global", "Global Chat")
        ]

        assert actual_chats == expected_chats

    def test_load_chatParticipants_data(self, game):
        test_game = game(TESTS_PATH / "test_set2/jhg_XJPV.json")
        test_game.cursor.execute("SELECT id FROM chatInfo")
        chat_ids = test_game.cursor.fetchall()

        expected_participants = [
            [(1,), (3,)],
            [(3,), (2,)],
            [(1,), (2,), (3,)]
        ]

        for i, chat_id in enumerate(chat_ids):
            test_game.cursor.execute("SELECT playerId FROM chatParticipants WHERE conversationId = ?", chat_id)
            actual_participants = test_game.cursor.fetchall()
            assert actual_participants == expected_participants[i]

    def test_load_messages_data(self, game):
        test_game = game(TESTS_PATH / "test_set2/jhg_XJPV.json")
        test_game.cursor.execute("SELECT * FROM messages")
        actual_messages = test_game.cursor.fetchall()

        expected_messages = [
            (1, 1, "-OS4sQ20LRln-2_0LASt", "Yankee", "Hi, Mike", "2025-06-06T15:35:08.227247Z", "identified"),
            (2, 1, "-OS4sSCopRs_Htr3CYGh", "Mike", "Hi, Yank", "2025-06-06T15:35:17.110586Z", "identified"),
            (3, 1, "-OS4sUhXW3zeuE4gvHEc", None, "Round 2", "2025-06-06T15:35:27.332050Z", "gameNotification"),

            (4, 2, "-OS4sUhcj2P8TMjlGkck", None, "Round 2", "2025-06-06T15:35:27.338517Z", "gameNotification"),

            (5, 3, "-OS4sM9wxGTEq2Y2SKNz", "Yankee", "Hey guys", "2025-06-06T15:34:52.349720Z", "identified"),
            (6, 3, "-OS4sNJMDVohmr20BKzs", "Tango", "sending 3 to both", "2025-06-06T15:34:57.049240Z", "identified"),
            (7, 3, "-OS4sRXDccbttAQ_Mw3-", "Yankee", "No", "2025-06-06T15:35:14.320444Z", "identified"),
            (8, 3, "-OS4sUhQ8NUCCToD81Qd", None, "Round 2", "2025-06-06T15:35:27.324972Z", "gameNotification"),
            (9, 3, "-OS4s_d-tzktuvpGOf9X", "Tango", "Alright, we have to tank yankee", "2025-06-06T15:35:51.618578Z",
             "identified"),
        ]

        assert actual_messages == expected_messages
