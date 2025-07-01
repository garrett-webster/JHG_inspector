from src.JHG_inspector.data_layer.DAOs.TableDao import TableDoa


class GamesetsDao(TableDoa):
    def __init__(self, connection):
        super().__init__(connection)

    def select_id(self, matching_columns, matching_vals):
        return self.select_one(["id"], matching_columns, matching_vals)[0]