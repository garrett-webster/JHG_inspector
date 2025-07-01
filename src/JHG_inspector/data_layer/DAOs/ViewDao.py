from abc import ABC

from src.JHG_inspector.data_layer.DAOs.TableDao import TableDoa


class ViewDao(TableDoa, ABC):
    def __init__(self, connection):
        super().__init__(connection)

    def insert(self, values):
        raise NotImplementedError("Cannot insert into a view")

    def insert_one(self, value):
        raise NotImplementedError("Cannot insert into a view")

    def delete(self, matching_columns, matching_vals):
        raise NotImplementedError("Cannot delete from a view")

    def delete_one(self, matching_column, matching_val):
        raise NotImplementedError("Cannot delete from a view")

    def select_id(self, matching_columns, matching_vals):
        raise NotImplementedError