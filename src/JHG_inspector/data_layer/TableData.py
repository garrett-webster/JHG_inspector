import json
from pathlib import Path

DB_INIT_FUNCTIONS = []
PATH = Path(__file__).parent


class TableData:
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
