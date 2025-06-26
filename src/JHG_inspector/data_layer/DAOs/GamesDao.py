from src.JHG_inspector.data_layer.DAOs.TableDao import TableDoa


class GamesDao(TableDoa):
    def __init__(self, connection):
        super().__init__(connection)

    def select_one(self):
        pass

    def select_all(self):
        pass