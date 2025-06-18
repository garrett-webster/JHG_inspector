from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow

from src.JHG_inspector.presentation_layer.dialogs.GamesDialog import GamesDialog
from src.JHG_inspector.presentation_layer.dialogs.GamesetsDialog import GamesetsDialog
from src.JHG_inspector.presentation_layer.panels.GamesetManager import GamesetManager


class MainWindow(QMainWindow):
    def __init__(self, database_access):
        super().__init__()
        self.database = database_access
        self.setWindowTitle('JHG Inspector')

        self.gameset_manager = GamesetManager(self.database)
        self.setCentralWidget(self.gameset_manager)


    def show_games(self):
        games_dialog = GamesDialog(self.database.games)
        games_dialog.exec()

    def show_gamesets(self):
        gamesets_dialog = GamesetsDialog(self.database)
        gamesets_dialog.setWindowTitle('Gamesets')
        gamesets_dialog.exec()