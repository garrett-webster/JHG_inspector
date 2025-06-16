from PyQt6.QtWidgets import QDialog


class GamesDialog(QDialog):
    def __init__(self, parent, games):
        super().__init__(parent)
        for game_id, game in games.items():
            print(game.code)