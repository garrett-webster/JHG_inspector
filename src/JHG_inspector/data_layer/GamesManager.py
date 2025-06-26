from sqlite3 import Connection


class GamesManager:
    def __init__(self, connection: Connection):
        self.connection = connection