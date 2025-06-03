# ---!--- #
# File for testing purposes only. Will be deleted later on. Nothing in here should be important for the program.
# ---!--- #

from pathlib import Path

from src.JHG_inspector.GameSet import GameSet
from src.JHG_inspector.JHGInspector import JHGInspector

FILE_PATH = Path(__file__).resolve().parent

if __name__=="__main__":
    with JHGInspector(base_path=FILE_PATH) as jhg_inspector:
        gameset = GameSet("testing", jhg_inspector.connection, jhg_inspector.get_next_gameset_id(), base_path=FILE_PATH)
        gameset.load_games(str(Path(FILE_PATH/"../../tests/test_set1").resolve()), base_path=Path(FILE_PATH))
