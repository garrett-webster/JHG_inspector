from functools import partial

from PyQt6.QtWidgets import QDialog, QPushButton, QVBoxLayout


class GamesDialog(QDialog):
    def __init__(self, games):
        super().__init__()
        self.setWindowTitle("Select A Game")
        self.selected = None
        layout = QVBoxLayout()
        self.setLayout(layout)

        for game_id, game in games.items():
            button = QPushButton(game.code)
            button.clicked.connect(partial(self.select_game, game))
            layout.addWidget(button)

    def select_game(self, game):
        self.selected = game
        self.accept()