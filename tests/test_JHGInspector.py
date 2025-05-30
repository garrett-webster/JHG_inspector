import json
from pathlib import Path

import pytest

from src.JHG_inspector.JHGInspector import JHGInspector


@pytest.fixture
def jhg_inspector(temp_folder):
    return JHGInspector()

@pytest.fixture
def temp_folder(tmp_path):
    test_folder = tmp_path / "test_games"
    test_folder.mkdir()
    yield test_folder

class TestJhgInspectorInitialization:
    def test_schema_columns_match_json(self, jhg_inspector):
        # Load schema from JSON
        schema_path = Path(__file__).parent.parent / "src" / "JHG_inspector" / "DB_commands" / "schema.json"
        with open(schema_path, "r") as f:
            expected_schema = json.load(f)

        cursor = jhg_inspector.connection.cursor()

        for table, expected_columns in expected_schema.items():
            cursor.execute(f"PRAGMA table_info({table})")
            actual_columns = [row[1] for row in cursor.fetchall()]  # row[1] = column name

            expected_column_names = list(expected_columns.keys())

            assert actual_columns == expected_column_names, (
                f"Mismatch in columns for table '{table}':\n"
                f"Expected: {expected_column_names}\n"
                f"Actual:   {actual_columns}"
            )