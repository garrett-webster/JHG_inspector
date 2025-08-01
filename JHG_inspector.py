import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from src.JHG_inspector.logic_layer.DatabaseManager import DatabaseManager
from src.JHG_inspector.logic_layer.ToolsManager import ToolsManager
from src.JHG_inspector.presentation_layer.MainWindow import MainWindow

FILE_PATH = Path(__file__).resolve().parent

if __name__ == "__main__":
    tools_manager = ToolsManager()
    database = DatabaseManager(tools_manager)
    app = QApplication(sys.argv)

    with open("src/JHG_inspector/presentation_layer/stylesheets/main.qss", "r") as f:
        app.setStyleSheet(f.read())


    window = MainWindow(database, tools_manager)
    app.main_window = window
    window.show()
    app.exec()