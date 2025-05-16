import json
import re
import sqlite3
from pathlib import Path

FILE_PATH = Path(__file__).resolve().parent


class Game:
    # base_path allows the tests to safely set up and tear down temporary paths.
    def __init__(self, game_path, base_path=FILE_PATH):
        self.path = game_path

        # Ensure that the game file actually exists and set the game code. If it does not exist, raise FileNotFoundError
        if not game_path.is_file():
            raise FileNotFoundError
        self.code = re.match(r"jhg_(.+)\.json", game_path.name).group(1)

        # Allow override of FILE_PATH
        self.db_path = base_path / "data_bases" / f"jhg_{self.code}.db"

        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Connect to the database. If it does not exist, create it.
        self.connection = None
        self.cursor = None

        needs_init = not self.db_path.is_file()
        self.connect_to_database()
        if needs_init:
            self.init_database()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def tables_exist(self):
        self.cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='players';
        """)
        return bool(self.cursor.fetchone())

    def connect_to_database(self):
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()

    def init_database(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS miscSettings(
            status TEXT,
            nameSet TEXT,
            chatType TEXT,
            messageType TEXT,
            creatorId TEXT
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS gameParams (
            lengthOfRound INTEGER,
            low INTEGER,
            high INTEGER,
            runtimeType TEXT
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS popularityFunctionParams (
            alpha REAL,
            beta REAL,
            cGive REAL,
            cKeep REAL,
            cSteal REAL,
            povertyLine REAL,
            shouldUseNewUpdate BOOL
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS governmentParams (
            initialPopularity REAL,
            initialPopularityType TEXT,
            randomPopularities TEXT,
            randomPopHigh REAL,
            randomPopLow REAL,
            playersThatWillBeGovernment TEXT,
            sendVotesImmediately BOOL
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS endCondition (
            duration INTEGER,
            runtimeType TEXT
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS rounds (
            id INTEGER PRIMARY KEY
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            name TEXT,
            experience TEXT,
            permissionLevel TEXT,
            color TEXT,
            hue TEXT,
            avatar TEXT,
            icon TEXT
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            round_id INTEGER,
            player_from_id INTEGER,
            player_to_id INTEGER,
            FOREIGN KEY(player_from_id) REFERENCES players(id),
            FOREIGN KEY(player_to_id) REFERENCES players(id),
            FOREIGN KEY(round_id) REFERENCES rounds(id)
        )""")

        # NOTE: If a player is in multiple groups, there will need to be multiple of these per round for that player
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS playerRoundInfo(
            player_id INTEGER,
            round_id INTEGER,
            numTokens INTEGER,
            group_name TEXT,
            FOREIGN KEY(player_id) REFERENCES players(id),
            FOREIGN KEY(round_id) REFERENCES rounds(id)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS popularities (
            player_id INTEGER,
            round_id INTEGER,
            popularity REAL,
            FOREIGN KEY(player_id) REFERENCES players(id),
            FOREIGN KEY(round_id) REFERENCES rounds(id)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS influences (
            player_from_id INTEGER,
            player_to_id INTEGER,
            round_id INTEGER,
            influence REAL,
            FOREIGN KEY(player_from_id) REFERENCES players(id),
            FOREIGN KEY(player_to_id) REFERENCES players(id),
            FOREIGN KEY(round_id) REFERENCES rounds(id)
        )""")

        self.connection.commit()


    # TODO: Add error handling to account for the possibility that a game file may have been corrupted (it will error with a keyerror potentially)
    def load_data_to_database(self):
        # Load game data
        with open(self.path, "r") as game_file:
            data = json.load(game_file)

        # Insert each player's record into the database
        for player in data["players"]:
            try:
                self.cursor.execute(
                    '''
                    INSERT INTO players (
                        name, experience, permissionLevel, color, hue, avatar, icon
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        player["name"],
                        player["experience"],
                        player["permissionLevel"],
                        player["color"],
                        player["hue"],
                        player["avatar"],
                        player["icon"]
                    )
                )
            except sqlite3.Error as e:
                print(f"Error inserting player {player['name']}: {e}")
        self.connection.commit()