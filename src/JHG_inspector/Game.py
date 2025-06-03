import json
import re
from pathlib import Path

from src.JHG_inspector.DB_commands.DB_init import get_schema, TableData

FILE_PATH = Path(__file__).resolve().parent

PLAYER_COLUMNS = ["name", "experience", "permissionLevel", "color", "hue", "avatar", "icon"]
PLAYER_COLUMN_TYPES = {
   "name": "TEXT",
   "experience": "INTEGER",
   "permissionLevel": "INTEGER",
   "color": "TEXT",
   "hue": "REAL",
   "avatar": "TEXT",
   "icon": "TEXT"
}


class Game:
   def __init__(self, connection, game_id, gameset_id, base_path=FILE_PATH):
       self.id_to_name_dict = {}
       self.initialized = False
       self.connection = connection
       self.cursor = connection.cursor()
       self.schema = get_schema(self.cursor)
       self.id = game_id
       self.gameset_id = gameset_id
       self.code = None

       self._set_id_to_name_dict()

   def _set_id_to_name_dict(self):
       self.cursor.execute("SELECT id, name FROM players WHERE gameId = ?", (self.id,))
       results = self.cursor.fetchall()

       for result in results:
           self.id_to_name_dict[result[0]] = result[1]

   def load_data_from_file(self, game_path):
       if not game_path.is_file():
           raise FileNotFoundError

       self.code = re.match(r"jhg_(.+)\.json", game_path.name).group(1)

       with open(game_path, "r") as game_file:
           data = json.load(game_file)

       self._load_metadata_and_config(data)
       self._load_player_data(data)
       self._set_id_to_name_dict()
       self.connection.commit()


   def _load_metadata_and_config(self, data):
       # table_data = TableData(self.schema["games"])
       # columns = table_data.non_key_columns


       # Minimum insert to get the ids tracking correctly
       code = data["lobby"]["code"]
       self.cursor.execute(
           "INSERT INTO games (gamesetId, code) VALUES (?, ?)",
           (self.gameset_id, code)
       )

   def _load_player_data(self, data):
       columns, column_names, placeholders = self._prepare_sql_strings("players")
       player_values = []

       for i, entry in enumerate(data["players"]):
           player_values.append((self.id, ) + tuple(entry[col[0]] for col in columns))
           self.id_to_name_dict[i + 1] = entry["name"]

       self.cursor.executemany(
           f"INSERT INTO players ({column_names}) VALUES ({placeholders})",
           player_values
       )

   def _prepare_sql_strings(self, table_name: str):
       table_data = TableData(self.schema[table_name])
       columns = table_data.non_key_columns
       column_names = ", ".join(["gameId"] + [column[0] for column in columns])
       placeholders = ", ".join(["?"] + ["?" for _ in columns])

       return columns, column_names, placeholders

