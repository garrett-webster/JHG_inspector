from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QToolBar


class InspectorToolbar(QToolBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)
        self.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea)

        games = QAction("Games", self)
        games.triggered.connect(parent.show_games)

        gamesets = QAction("Gamesets", self)
        gamesets.triggered.connect(parent.show_gamesets)

        self.addAction(games)
        self.addAction(gamesets)