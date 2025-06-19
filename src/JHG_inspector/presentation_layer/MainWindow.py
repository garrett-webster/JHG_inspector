from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QStatusBar, QDialog, QSplitter

from src.JHG_inspector.presentation_layer.dialogs.GamesDialog import GamesDialog
from src.JHG_inspector.presentation_layer.panels.GamesetManager import GamesetManager
from src.JHG_inspector.presentation_layer.panels.Panel import Panel


class MainWindow(QMainWindow):
    def __init__(self, database_access):
        super().__init__()
        self.database = database_access
        self.setWindowTitle('JHG Inspector')
        self.gameset_manager = GamesetManager(self.database)

        self.setStatusBar(QStatusBar())
        self.add_menubar()

        self.central_panel = Panel(self)

        self.body_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.body_splitter.addWidget(self.gameset_manager)
        self.body_splitter.addWidget(self.central_panel)
        self.body_splitter.setCollapsible(0, False)

        self.setCentralWidget(self.body_splitter)


    def add_menubar(self):
        menubar = self.menuBar()
        def add_menu_action(menu, title, function, tooltip: str = ""):
            new_action = QAction(title, self)
            new_action.triggered.connect(function)
            new_action.setStatusTip(tooltip)
            new_action.setToolTip(tooltip)
            menu.addAction(new_action)

        # Game menu
        games_menu = menubar.addMenu('Games')
        add_menu_action(games_menu, 'Show Games', self.show_games, "Show all loaded games in a new window")
        add_menu_action(games_menu, 'Load Game From File', self.load_game_file, "Load a new game to the database from a JHG gamelog")
        add_menu_action(games_menu, "Load Games From Folder", self.load_games_from_directory, "Load all game logs from a folder to the database")

        # Gameset menu
        gamesets_menu = menubar.addMenu('Gamesets')
        add_menu_action(gamesets_menu, 'Show/Hide Gamesets', self.show_hide_gamesets, "Toggles the gameset sidebar")
        add_menu_action(gamesets_menu, "New Gameset", self.gameset_manager.add_gameset, "Create a new gameset")

    # --- QAction functions --- #
    def show_games(self):
        games_dialog = GamesDialog(self.database.games)
        games_dialog.exec()

    def load_game_file(self):
        dialog = QFileDialog()
        if dialog.exec() == 1:
            self.database.load_game_from_file(Path(dialog.selectedFiles()[0]))

    def load_games_from_directory(self):
        directory_path = QFileDialog.getExistingDirectory(options=QFileDialog.Option.ShowDirsOnly)

        if directory_path:
            self.database.load_games_from_directory(Path(directory_path))

    def show_hide_gamesets(self):
        if self.gameset_manager.isVisible():
            self.gameset_manager.hide()
        else:
            self.gameset_manager.show()