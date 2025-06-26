from sqlite3 import Connection


class GamesetManager:
    def __init__(self, connection: Connection):
        self.connection = connection