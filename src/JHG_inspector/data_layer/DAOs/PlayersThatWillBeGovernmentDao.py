from src.JHG_inspector.data_layer.DAOs.TableDao import TableDoa


class PlayersThatWillBeGovernmentDao(TableDoa):
    def __init__(self, connection):
        super().__init__(connection)

    def select_id(self, matching_columns, matching_vals):
        raise NotImplemented