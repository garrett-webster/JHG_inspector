import json
from pathlib import Path

DB_INIT_FUNCTIONS = []
PATH = Path(__file__).parent

def initialize_DB(cursor):
    schemas = get_schema(cursor)

    # Load each table from the schema.json and create the table
    for table_name, columns_dict in schemas.items():
        columns = ", ".join(f"{col} {col_type}" for col, col_type in columns_dict.items())
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")

def get_schema(cursor) -> dict:
    with open(PATH / "schema.json", "r") as f:
        return json.load(f)
