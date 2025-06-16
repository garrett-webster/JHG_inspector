from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow

from src.JHG_inspector.presentation_layer.dialogs.GamesDialog import GamesDialog
from src.JHG_inspector.presentation_layer.dialogs.GamesetsDialog import GamesetsDialog
from src.JHG_inspector.presentation_layer.InspectorToolbar import InspectorToolbar


class MainWindow(QMainWindow):
    def __init__(self, database_access):
        super().__init__()
        self.database = database_access
        self.setWindowTitle('JHG Inspector')

        self.toolbar = InspectorToolbar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

    def show_games(self):
        games_dialog = GamesDialog(self, self.database.games)
        games_dialog.setWindowTitle('Loaded Games')
        games_dialog.exec()

    def show_gamesets(self):
        gamesets_dialog = GamesetsDialog(self, self.database.gamesets)
        gamesets_dialog.setWindowTitle('Loaded Gamesets')
        gamesets_dialog.exec()