import json
import sqlite3
from pathlib import Path

from src.JHG_inspector.data_layer.DAOs.Gameset_gamesDao import Gameset_gamesDao
from src.JHG_inspector.data_layer.DAOs.AdminsDao import AdminsDao
from src.JHG_inspector.data_layer.DAOs.ChatInfoDao import ChatInfoDao
from src.JHG_inspector.data_layer.DAOs.ChatParticipantsDao import ChatParticipantsDao
from src.JHG_inspector.data_layer.DAOs.GamesGameset_gamesDao import GamesGameset_gamesDao
from src.JHG_inspector.data_layer.DAOs.GamesetsDao import GamesetsDao
from src.JHG_inspector.data_layer.DAOs.GroupsDao import GroupsDao
from src.JHG_inspector.data_layer.DAOs.Groups_PlayersDao import Groups_playersDao
from src.JHG_inspector.data_layer.DAOs.InfluencesDao import InfluencesDao
from src.JHG_inspector.data_layer.DAOs.MessagesDao import MessagesDao
from src.JHG_inspector.data_layer.DAOs.PlayerRoundInfoDao import PlayerRoundInfoDao
from src.JHG_inspector.data_layer.DAOs.PlayersDao import PlayersDao
from src.JHG_inspector.data_layer.DAOs.GamesDao import GamesDao
from src.JHG_inspector.data_layer.DAOs.PlayersThatWillBeGovernmentDao import PlayersThatWillBeGovernmentDao
from src.JHG_inspector.data_layer.DAOs.PopularitiesDao import PopularitiesDao
from src.JHG_inspector.data_layer.DAOs.SearchTagsDao import SearchTagsDao
from src.JHG_inspector.data_layer.DAOs.TransactionsDao import TransactionsDao
from src.JHG_inspector.data_layer.DAOs.ColorGroupsDao import ColorGroupsDao
from src.JHG_inspector.data_layer.TableData import TableData
from src.JHG_inspector.logic_layer.GamesetManager import GamesetManager
from src.JHG_inspector.logic_layer.GamesManager import GamesManager
from src.JHG_inspector.logic_layer.ToolsManager import ToolsManager

PATH = Path(__file__).parent

FILE_PATH = Path(__file__).resolve().parent

DAO_CLASSES = {
    "searchTags": SearchTagsDao,
    "players": PlayersDao,
    "games": GamesDao,
    "admins": AdminsDao,
    "playersThatWillBeGovernment": PlayersThatWillBeGovernmentDao,
    "colorGroups": ColorGroupsDao,
    "transactions": TransactionsDao,
    "popularities": PopularitiesDao,
    "groups": GroupsDao,
    "groups_players": Groups_playersDao,
    "influences": InfluencesDao,
    "chatInfo": ChatInfoDao,
    "chatParticipants": ChatParticipantsDao,
    "messages": MessagesDao,
    "playerRoundInfo": PlayerRoundInfoDao,

    "gamesets": GamesetsDao,
    "GamesGameset_gamesDao": GamesGameset_gamesDao,
    "gameset_games": Gameset_gamesDao
}

class DatabaseManager:
    """DatabaseManager is the single point through which the logic layer and presentation layers interact with the
       database, through the database access objects (DAOs) that the DatabaseManager holds.

       The DatabaseManager holds the connection to the database that is used by the entire program. Additionally, it
       stores references to the GamesManager and GamesetManagers, which are used to send specific commands to the DAOs
       that the DatabaseManager object holds.
       """

    def __init__(self, tools_manager: ToolsManager, database_path = FILE_PATH.parent / "data_bases" / f"JHGInspector.db"):
        self.connection = self.connect(database_path)
        self.DAOs = {name: DAO(self.connection) for name, DAO in DAO_CLASSES.items()}

        self.games = GamesManager(self)
        self.gamesets = GamesetManager(self, tools_manager)

    def __enter__(self, base_path=FILE_PATH):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    # TODO: Set this up to be able to connect to a different data base, closing the previous connection if one exists
    def connect(self, database_path):
        """Connect to the database file found at the path passed in database_path"""
        database_path.parent.mkdir(parents=True, exist_ok=True)

        connection = sqlite3.connect(str(database_path))
        connection.execute("PRAGMA foreign_keys = ON")

        self.initialize_DB(connection)

        return connection

    def initialize_DB(self, connection):
        with open(f"{PATH.parent}/data_layer/schema.json", "r") as f:
            schemas = json.load(f)

        cursor = connection.cursor()

        for table_name, table_def in schemas.items():
            table_data = TableData(table_def)
            column_lines = []

            for col, col_type in table_data.columns:
                column_lines.append(f"{col} {col_type}")

            for fk in table_data.foreign_keys:
                column_lines.append(
                    f"FOREIGN KEY({fk['column']}) REFERENCES {fk['references']['table']}({fk['references']['column']})"
                )

            columns_sql = ", ".join(column_lines)
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})")