from PyQt6.QtWidgets import QWidget, QVBoxLayout


class GameInspectorView(QWidget):
    def __init__(self, game: "Game"):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.game = game