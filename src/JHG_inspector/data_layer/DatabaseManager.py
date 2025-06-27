import sqlite3
from pathlib import Path

from src.JHG_inspector.data_layer.DAOs.AdminsDao import AdminsDao
from src.JHG_inspector.data_layer.DAOs.ChatInfoDao import ChatInfoDao
from src.JHG_inspector.data_layer.DAOs.ChatParticipantsDao import ChatParticipantsDao
from src.JHG_inspector.data_layer.DAOs.GroupsDao import GroupsDao
from src.JHG_inspector.data_layer.DAOs.InfluencesDao import InfluencesDao
from src.JHG_inspector.data_layer.DAOs.MessagesDao import MessagesDao
from src.JHG_inspector.data_layer.DAOs.PlayersDao import PlayersDao
from src.JHG_inspector.data_layer.DAOs.GamesDao import GamesDao
from src.JHG_inspector.data_layer.DAOs.PlayersThatWillBeGovernmentDao import PlayersThatWillBeGovernmentDao
from src.JHG_inspector.data_layer.DAOs.PopularitiesDao import PopularitiesDao
from src.JHG_inspector.data_layer.DAOs.SearchTagsDao import SearchTagsDao
from src.JHG_inspector.data_layer.DAOs.TransactionsDao import TransactionsDao
from src.JHG_inspector.data_layer.DAOs.ColorGroupsDao import ColorGroupsDao
from src.JHG_inspector.data_layer.DB_init import initialize_DB
from src.JHG_inspector.data_layer.GamesManager import GamesManager
from src.JHG_inspector.data_layer.GamesetManager import GamesetManager

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
    "influences": InfluencesDao,
    "chatInfo": ChatInfoDao,
    "chatParticipants": ChatParticipantsDao,
    "messages": MessagesDao,
}

class DatabaseManager:
    def __init__(self, base_path=FILE_PATH):
        self.connection = self.connect(base_path)
        self.DAOs = {name: DAO(self.connection) for name, DAO in DAO_CLASSES.items()}

        self.gameset = GamesetManager(self.connection)
        self.games = GamesManager(self.connection)

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
    def connect(self, base_path):
        # Connect to the database
        db_path = base_path.parent / "data_bases" / f"JHGInspector.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        connection = sqlite3.connect(str(db_path))
        connection.execute("PRAGMA foreign_keys = ON")

        initialize_DB(connection)

        return connection