from functools import partial

from PyQt6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QLabel


class GamesDialog(QDialog):
    """Used to display the loaded games.

       If a gameset is passed in, then it is being used to add games to a gameset. In that case, filters out the games
       already added to that gameset and adds buttons to select that game. If not gameset is passed, simply display all
       the loaded games.
       """

    def __init__(self, games, gameset=None, parent=None):
        super().__init__(parent)
        self.selected = None
        layout = QVBoxLayout()
        self.setLayout(layout)

        if gameset:
            # If a gameset is passed (adding games) filter out the games that are already in the gameset
            self.setWindowTitle("Select A Game")
            for game_id, game in games.items():
                if gameset.games.get(game_id) is None:
                    button = QPushButton(game.code)
                    button.clicked.connect(partial(self.select_game, game))
                    layout.addWidget(button)
        else:
            # No gameset passed (used to display games)
            self.setWindowTitle('Loaded Games')
            for game_id, game in games.all.items():
                layout.addWidget(QLabel(game.code))


    def select_game(self, game):
        self.selected = game
        self.accept()