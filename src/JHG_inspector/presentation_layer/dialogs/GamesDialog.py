from functools import partial

from PyQt6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QWidget, QRadioButton, QCheckBox


class GamesDialog(QDialog):
    """Used to display the loaded games.

       If a gameset is passed in, then it is being used to add games to a gameset. In that case, filters out the games
       already added to that gameset and adds buttons to select that game. If no gameset is passed, display all the
       loaded games.
       """

    def __init__(self, games, gameset=None, parent=None):
        super().__init__(parent)
        with open("src/JHG_inspector/presentation_layer/stylesheets/GamesDialog.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.selected = None
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        if gameset:
            self.gameset = gameset
            self.updated_games = gameset.games.copy()

            self.setWindowTitle('Select Games')
            for game_id, game in games.all.items():
                row = QWidget()
                row_layout = QHBoxLayout()
                label = QLabel(game.code)
                selected_button = QCheckBox()

                row_layout.addWidget(label)
                row_layout.addWidget(selected_button)
                row.setLayout(row_layout)

                is_in_gameset = game in gameset.games.values()
                selected_button.setChecked(is_in_gameset)

                selected_button.clicked.connect(partial(self.select_game, game, selected_button))
                layout.addWidget(row)
        else:
            self.setWindowTitle('Loaded Games')
            for game_id, game in games.all.items():
                layout.addWidget(QLabel(game.code))

    def select_game(self, game, button):
        if game not in self.updated_games.values():
            self.updated_games[game.id] = game
            button.setProperty("selected", True)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()
        else:
            self.updated_games.pop(game.id)
            button.setProperty("selected", False)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()