from functools import partial

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QFormLayout, QSizePolicy, QHBoxLayout

from src.JHG_inspector.data_layer.Game import Game
from src.JHG_inspector.data_layer.Gameset import Gameset


class GamesetElement(QWidget):
    def __init__(self, title: str, gameset: Gameset, select_game, remove_game):
        super().__init__()

        self.toggle_button = QPushButton(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)

        self.content = GamesList(gameset, select_game, remove_game)
        self.content.setVisible(False)

        self.toggle_button.clicked.connect(self.toggle_content)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content)
        self.setLayout(layout)

    def toggle_content(self):
        is_expanded = self.toggle_button.isChecked()
        self.content.setVisible(is_expanded)

    def get_smallest_width(self):
        return self.content.get_smallest_width()

class GamesList(QWidget):
    def __init__(self, gameset, select_game, remove_game):
        super().__init__()
        self.remove_game = remove_game
        self.gameset = gameset
        self.buttons = []

        self.layout = QVBoxLayout()

        header = QHBoxLayout()
        header.addWidget(QLabel("Game Code"))
        add_game_button = QPushButton("Add Game")
        add_game_button.clicked.connect(partial(select_game, gameset))

        header.addWidget(add_game_button)
        self.layout.addLayout(header)

        self.game_rows = {}
        for game in gameset.games.values():
            self.add_game(game)

        self.setLayout(self.layout)

    def add_game(self, game: Game):
        self.game_rows[game.id] = QHBoxLayout() #(QLabel(game.code))
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(partial(self.remove_game, self.gameset, game))
        delete_button.setSizePolicy(
            QSizePolicy.Policy.Maximum,  # no stretching horizontally
            QSizePolicy.Policy.Fixed  # no stretching vertically
        )
        self.buttons.append(delete_button)

        self.game_rows[game.id].addWidget(QLabel(game.code))
        self.game_rows[game.id].addWidget(delete_button)

        self.layout.addLayout(self.game_rows[game.id])

    def remove_game_item(self, game: Game):
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

    def get_smallest_width(self):
        if not self.buttons:
            return QSize(100, 800)  # fallback

        min_width = min(btn.sizeHint().width() for btn in self.buttons)
        return QSize(min_width, 800)