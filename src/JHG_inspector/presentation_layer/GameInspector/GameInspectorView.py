from PyQt6.QtWidgets import QWidget, QVBoxLayout

from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum


class GameInspectorView(QWidget):
    def __init__(self, game: "Game"):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.game = game

    def update_scope(self, scope: ScopesEnum):
        raise NotImplementedError("Subclasses must implement update_scope")