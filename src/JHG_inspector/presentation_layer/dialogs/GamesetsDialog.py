from PyQt6.QtWidgets import QDialog


class GamesetsDialog(QDialog):
    def __init__(self, parent, gamesets):
        super().__init__(parent)
        for gameset_id, gameset in gamesets.items():
            print(gameset.name)