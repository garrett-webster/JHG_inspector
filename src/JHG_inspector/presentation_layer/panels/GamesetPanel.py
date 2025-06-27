from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QSizePolicy, QDialog

from src.JHG_inspector.data_layer.Game import Game
from src.JHG_inspector.data_layer.Gameset import Gameset
from src.JHG_inspector.presentation_layer.dialogs.GamesDialog import GamesDialog
from src.JHG_inspector.presentation_layer.components.GamesetElement import GamesetElement
from src.JHG_inspector.presentation_layer.dialogs.NewGamesetDialog import NewGamesetDialog
from src.JHG_inspector.presentation_layer.panels.Panel import Panel


class GamesetPanel(Panel):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.gameset_elements = {}

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(content_widget)

        wrapper_layout = QVBoxLayout(self)
        wrapper_layout.addWidget(scroll_area)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        for gameset in database.gamesets.values():
            self.add_gameset_section(gameset.name, gameset)

    def add_gameset(self):
        dialog = NewGamesetDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:

            name = dialog.name
            new_gameset = self.database.create_gameset(name)

            if dialog.directory_path:
                path = Path(dialog.directory_path)
                self.database.load_games_from_directory(path, gameset=new_gameset)

            self.add_gameset_section(name, new_gameset)

    def remove_gameset(self, gameset: Gameset):
        self.database.delete_gameset(gameset)
        self.gameset_elements[gameset.id].deleteLater()
        del self.gameset_elements[gameset.id]

    def add_gameset_section(self, title: str, gameset: Gameset):
        section = GamesetElement(title, gameset, self.add_game_via_dialog, self.remove_game, self.remove_gameset)
        section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.gameset_elements[gameset.id] = section
        self.layout.addWidget(section)

    def add_game_via_dialog(self, gameset):
        games_list = self.gameset_elements[gameset.id].content

        dialog = GamesDialog(self.database.games, gameset, parent=self.window())
        dialog.setWindowFlag(Qt.WindowType.Tool)  # <-- Tool windows don’t drag the parent
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        if dialog.exec() == 1:
            game = dialog.selected
            if game != gameset.games.get(game.id):
                gameset.add_game(game.id) # Adds the game on the backend
                games_list.add_game(game) # Adds the game on the frontend

    def remove_game(self, gameset: Gameset, game: Game):
        gameset.remove_game(game.id)
        games_list = self.gameset_elements[gameset.id].content
        games_list.remove_game_item(game)

    def sizeHint(self):
        return QSize(150, 800)
