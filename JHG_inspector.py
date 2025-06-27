import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from src.JHG_inspector.logic_layer.DatabaseManager import DatabaseManager
from src.JHG_inspector.presentation_layer.MainWindow import MainWindow

FILE_PATH = Path(__file__).resolve().parent

if __name__ == "__main__":
    database = DatabaseManager(Path(FILE_PATH) / "src" / "JHG_inspector")
    app = QApplication(sys.argv)

    window = MainWindow(database)
    window.show()
    app.exec()