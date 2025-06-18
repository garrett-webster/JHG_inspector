from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QSizePolicy

from src.JHG_inspector.data_layer.Game import Game
from src.JHG_inspector.data_layer.Gameset import Gameset
from src.JHG_inspector.presentation_layer.dialogs.GamesDialog import GamesDialog
from src.JHG_inspector.presentation_layer.dialogs.GamesetElement import GamesetElement
from src.JHG_inspector.presentation_layer.panels.Panel import Panel


class GamesetManager(Panel):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.gameset_elements = {}

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(content_widget)

        wrapper_layout = QVBoxLayout(self)
        wrapper_layout.addWidget(scroll_area)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        for gameset in database.gamesets.values():
            self.add_gameset_section(gameset.name, gameset, database)

    def add_gameset_section(self, title: str, gameset: Gameset, database):
        section = GamesetElement(title, gameset, self.add_game_via_dialog, self.remove_game)
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
            if game == gameset.games.get(game.id):
                print("ERRRR!!")
            else:
                gameset.add_game(game.id) # Adds the game on the backend
                games_list.add_game(game) # Adds the game on the frontend


    def remove_game(self, gameset: Gameset, game: Game):
        gameset.remove_game(game.id)
        games_list = self.gameset_elements[gameset.id].content
        games_list.remove_game_item(game)

    def sizeHint(self):
        if not self.gameset_elements:
            return QSize(100, 800)

        # min_width = min(element.sizeHint().width for element in self.gameset_elements)
        return QSize(100, 800)
