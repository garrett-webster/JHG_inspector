from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QStatusBar, QSplitter

from src.JHG_inspector.logic_layer.DatabaseManager import DatabaseManager
from src.JHG_inspector.logic_layer.ToolsManager import ToolsManager
from src.JHG_inspector.presentation_layer.Container import Container
from src.JHG_inspector.presentation_layer.dialogs.GamesDialog import GamesDialog
from src.JHG_inspector.presentation_layer.dialogs.OpenToolDialog import OpenToolDialog
from src.JHG_inspector.presentation_layer.panels.CentralContainer import CentralContainer
from src.JHG_inspector.presentation_layer.panels.GamesetPanel import GamesetPanel


class MainWindow(QMainWindow):
    def __init__(self, database: DatabaseManager, tools_manager: ToolsManager):
        super().__init__()
        self.database = database
        self.tools_manager = tools_manager
        self.setWindowTitle('JHG Inspector')
        self.gamesets_panel = GamesetPanel(self.database)

        self.setStatusBar(QStatusBar())
        self.add_menubar()

        self.central_panel = CentralContainer(self)
        # TODO: Pass self.selected_panel down the line to allow for setting the selected panel easier
        self.selected_panel: Container = self.central_panel

        # Adds the gameset panel to the left and designates the rest as the main area for panels
        self.body_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.body_splitter.addWidget(self.gamesets_panel)
        self.body_splitter.addWidget(self.central_panel)

        # Tells the splitter to keep the gameset panel the same size when the window is resized
        self.body_splitter.setStretchFactor(0, 0)
        self.body_splitter.setStretchFactor(1, 1)
        self.body_splitter.setCollapsible(0, False)

        self.setCentralWidget(self.body_splitter)

    def add_menubar(self):
        """Adds the menubar to the top and attaches the relevant function."""
        menubar = self.menuBar()

        def add_menu_action(menu, title, function, tooltip: str = ""):
            """Adds a single action to a menu in the menubar.

            Parameters
            ----------
            menu : QMenu
                The menu to add the action to.
            title : str
                The title of the action to be displayed in the menu.
            function : function
                The function to be called when the menu item is clicked.
            tooltip: str
                The message to be displayed in the status bar at the bottom of the GUI when a menu item is hovered over
            """

            new_action = QAction(title, self)
            new_action.triggered.connect(function)
            new_action.setStatusTip(tooltip)
            new_action.setToolTip(tooltip)
            menu.addAction(new_action)

        # Game menu
        games_menu = menubar.addMenu('Games')
        add_menu_action(games_menu, 'Show Games', self.show_games, "Show all loaded games in a new window")
        add_menu_action(games_menu, 'Load Game From File', self.load_game_file,
                        "Load a new game to the database from a JHG gamelog")
        add_menu_action(games_menu, "Load Games From Folder", self.load_games_from_directory,
                        "Load all game logs from a folder to the database")

        # Gameset menu
        gamesets_menu = menubar.addMenu('Gamesets')
        add_menu_action(gamesets_menu, 'Show/Hide Gamesets', self.toggle_gamesets_panel, "Toggles the gameset sidebar")
        add_menu_action(gamesets_menu, "New Gameset", self.gamesets_panel.add_gameset, "Create a new gameset")

        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        add_menu_action(tools_menu, 'Open Tool', self.open_tool, "Open a tool in a new panel")

    # --- QAction functions --- #
    def show_games(self):
        """Opens a modal that displays all loaded games"""
        games_dialog = GamesDialog(self.database.games)
        games_dialog.exec()

    def load_game_file(self):
        """Opens a modal to select a path to a game log file. If one is chosen, loads that game into the database"""
        dialog = QFileDialog()
        if dialog.exec() == 1:
            self.database.games.load_game_from_file(Path(dialog.selectedFiles()[0]))

    def load_games_from_directory(self):
        """Opens a modal to select a path to a directory. If one is chosen, loads all the game log files in that
           directory into the database"""
        directory_path = QFileDialog.getExistingDirectory(options=QFileDialog.Option.ShowDirsOnly)

        if directory_path:
            self.database.games.load_games_from_directory(Path(directory_path))

    def toggle_gamesets_panel(self):
        """Toggles the visibility of the gamesets panel"""
        if self.gamesets_panel.isVisible():
            self.gamesets_panel.hide()
        else:
            self.gamesets_panel.show()

    def open_tool(self):
        """Opens a modal that lets you select a tool to open and a gameset to attach to it"""
        dialog = OpenToolDialog(self, self.database.gamesets.all.values(), self.tools_manager.tools_types_list)
        if dialog.exec():
            tool = self.tools_manager.new_tool(self.selected_panel, dialog.tool, dialog.gameset)

            self.selected_panel.split(tool.view)