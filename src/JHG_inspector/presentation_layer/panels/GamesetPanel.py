from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QSizePolicy, QDialog, QLabel, QFrame, QMessageBox

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.logic_layer.Gameset import Gameset
from src.JHG_inspector.presentation_layer.dialogs.GamesDialog import GamesDialog
from src.JHG_inspector.presentation_layer.components.GamesetElement import GamesetElement
from src.JHG_inspector.presentation_layer.dialogs.NewGamesetDialog import NewGamesetDialog
from src.JHG_inspector.presentation_layer.panels.Panel import Panel


class GamesetPanel(QWidget):
    """A side panel that shows all the gamesets and their games, and allows editing those gamesets."""
    def __init__(self, database):
        super().__init__()
        with open("src/JHG_inspector/presentation_layer/stylesheets/GamesetPanel.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.database = database
        self.gameset_elements = {}

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        header = QLabel("Gamesets")
        header.setObjectName("headerLabel")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.layout.addWidget(header)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(line)

        scroll_area.setWidget(content_widget)

        wrapper_layout = QVBoxLayout(self)
        wrapper_layout.addWidget(scroll_area)
        wrapper_layout.setSpacing(0)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        for gameset in database.gamesets.all.values():
            self.add_gameset_section(gameset.name, gameset)

    def add_gameset(self):
        dialog = NewGamesetDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:

            name = dialog.name
            new_gameset = self.database.gamesets.create_gameset(name)

            if dialog.directory_path:
                path = Path(dialog.directory_path)
                self.database.games.load_games_from_directory(path, gameset=new_gameset)

            self.add_gameset_section(name, new_gameset)

    def remove_gameset(self, gameset: Gameset):
        self.database.gamesets.delete_gameset(gameset)
        self.gameset_elements[gameset.id].deleteLater()
        del self.gameset_elements[gameset.id]

    def add_gameset_section(self, title: str, gameset: Gameset):
        section = GamesetElement(title, gameset, self.add_game_via_dialog, self.remove_game_with_confirmation, self.remove_gameset)
        section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.gameset_elements[gameset.id] = section
        self.layout.addWidget(section)

    def add_game_via_dialog(self, gameset: Gameset):
        games_list = self.gameset_elements[gameset.id].content

        dialog = GamesDialog(self.database.games, gameset, parent=self.window())
        dialog.setWindowFlag(Qt.WindowType.Tool)  # <-- Tool windows don’t drag the parent
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.exec()

        if gameset.games != dialog.updated_games:
            new_games = dialog.updated_games.items() - gameset.games.items()
            games_to_remove = gameset.games.items() - dialog.updated_games.items()

            for new_game in new_games:
                gameset.add_game(new_game[1].id)  # Adds the game on the backend
                games_list.add_game(new_game[1])  # Adds the game on the frontend

            for game_to_remove in games_to_remove:
                self.remove_game(gameset, game_to_remove[1])

    def remove_game_with_confirmation(self, gameset: Gameset, game:Game):
        result = QMessageBox.question(
            self,
            f"Remove {game.code} From Gameset",
            "Are you sure you want to remove this game?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if result == QMessageBox.StandardButton.Yes:
            self.remove_game(gameset, game)

    def remove_game(self, gameset: Gameset, game: Game):
        gameset.remove_game(game.id)
        games_list = self.gameset_elements[gameset.id].content
        games_list.remove_game_item(game)
        self.database.gamesets.update_signal(gameset.id)

    def sizeHint(self):
        return QSize(150, 800)
