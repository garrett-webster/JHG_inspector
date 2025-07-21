from functools import partial

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QMessageBox, QWidget

from src.JHG_inspector.logic_layer.Game import Game


class GamesList(QWidget):
    def __init__(self, gameset, delete_button, select_game, remove_game):
        super().__init__()
        self.remove_game = remove_game
        self.gameset = gameset
        self.buttons = []

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)


        self.game_rows = {}
        for game in gameset.games.values():
            self.add_game(game)

        self.setLayout(self.layout)

    def add_game(self, game: Game):
        self.game_rows[game.id] = QHBoxLayout()
        self.game_rows[game.id].setSpacing(0)
        self.game_rows[game.id].setContentsMargins(0, 0, 0, 0)

        delete_button = QPushButton(game.code)
        delete_button.clicked.connect(partial(self.remove_game, self.gameset, game))
        delete_button.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed
        )

        #Style the button
        delete_button.setProperty("class", "GameListButton")
        delete_button.style().unpolish(delete_button)
        delete_button.style().polish(delete_button)
        delete_button.setMinimumWidth(0)
        delete_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.buttons.append(delete_button)

        self.game_rows[game.id].addWidget(delete_button)

        self.layout.addLayout(self.game_rows[game.id])

    def remove_game_item(self, game: Game):
        result = QMessageBox.question(
            self,
            f"Remove {game.code} From Gameset",
            "Are you sure you want to remove this game?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if result == QMessageBox.StandardButton.Yes:
            row = self.game_rows[game.id]
            while row.count():
                item = row.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                    widget.deleteLater()

            self.layout.removeItem(row)
            row.deleteLater()
            del self.game_rows[game.id]