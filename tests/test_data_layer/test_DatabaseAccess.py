from pathlib import Path

from tests.test_data_layer.data_layer_testing_utilities import *

class TestJhgInspectorInitialization:
    def test_schema_columns_match_json(self, database_access):
        # Load schema from JSON
        schema_path = Path(__file__).parent.parent.parent / "src" / "JHG_inspector" / "data_layer" / "DB_commands" / "schema.json"
        with open(schema_path, "r") as f:
            expected_schema = json.load(f)

        cursor = database_access.connection.cursor()

        for table, expected_columns in expected_schema.items():
            cursor.execute(f"PRAGMA table_info({table})")
            actual_columns = [row[1] for row in cursor.fetchall()]  # row[1] = column name

            expected_column_names = [key for key in expected_columns.keys() if key not in ('FOREIGN_KEYS', 'FOREIGN_KEYS_EXCLUDE')]

            assert set(actual_columns) == set(expected_column_names), (
                f"Mismatch in columns for table '{table}':\n"
                f"Expected: {sorted(expected_column_names)}\n"
                f"Actual:   {sorted(actual_columns)}"
            )