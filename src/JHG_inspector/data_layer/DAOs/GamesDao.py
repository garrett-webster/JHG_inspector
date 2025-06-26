from src.JHG_inspector.data_layer.DAOs.TableDao import TableDoa, set_sql_strings


@set_sql_strings
class GamesDao(TableDoa):
    def __init__(self, connection):
        super().__init__(connection)

    def insert(self, values):
        pass

    def select_one(self):
        pass

    def select_all(self):
        pass