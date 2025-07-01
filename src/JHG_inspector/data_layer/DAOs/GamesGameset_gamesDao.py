from src.JHG_inspector.data_layer.DAOs.ViewDao import ViewDao


class GamesGameset_gamesDao(ViewDao):
    def __init__(self, connection):
        super().__init__(connection)

    def select(self, select_columns: list[str], matching_columns: list[str], matching_vals: list):
        select_columns_string = ", ".join(select_columns)

        cursor = self.connection.cursor()

        if matching_columns:
            matching_columns_string = " AND ".join([column + " = ?" for column in matching_columns])
            return cursor.execute(f"SELECT {select_columns_string} FROM games JOIN gameset_games ON "
                      f"games.id = gameset_games.gameId WHERE {matching_columns_string}",
                       matching_vals)
        else:
            return cursor.execute(
                f"SELECT {select_columns_string} FROM games JOIN gameset_games ON "
                      "games.id = gameset_games.gameId", matching_vals)

    @classmethod
    def prepare_sql_strings(cls):
        """Because you cannot insert into a view, the prepare_sql_strings method is not needed, but not overriding it
           creates issues because "gamesGameset_gamesDao" is not a table in the schema"""
        ...