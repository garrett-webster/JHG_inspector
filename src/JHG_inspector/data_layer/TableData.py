import json
from pathlib import Path

DB_INIT_FUNCTIONS = []
PATH = Path(__file__).parent


class TableData:
    """Represents the structure of a table in the database, as defined in the schema.json.

       Defines the following attributes:
          columns: list[tuple[str, str]]
            A list of tuples of strings containing the name and data type of a column in the table.
          foreign_keys: list[dict]
            A list of dictionaries defining which columns are the foreign keys of the table and which table and column
            they reference.
          primary_key: tuple[str, str]
            Contains the name of the column that will be the primary key of the table and its type.
       """
    def __init__(self, table):
        self.columns = []
        self.foreign_keys = []
        self.primary_key = None
        fk_data = table.get("FOREIGN_KEYS", [])
        fk_exclude_data = table.get("FOREIGN_KEYS_EXCLUDE", [])

        for column, data_type in table.items():
            if column in ("FOREIGN_KEYS", "FOREIGN_KEYS_EXCLUDE"):
                continue
            if "PRIMARY KEY" in data_type:
                self.primary_key = (column, data_type)
            self.columns.append((column, data_type))

        self.non_excluded_columns = self.columns.copy()
        for fk in fk_data:
            self.foreign_keys.append(fk)
            # Removes any foreign keys from the column list so you are left with only the non key columns

        excluded_columns = {fk["column"] for fk in fk_exclude_data}
        self.non_excluded_columns = [col for col in self.columns if col[0] not in excluded_columns]

        if self.primary_key:
            self.non_excluded_columns.remove(self.primary_key)
