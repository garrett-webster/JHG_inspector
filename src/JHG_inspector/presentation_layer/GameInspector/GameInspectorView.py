from PyQt6.QtWidgets import QWidget, QVBoxLayout

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum

def update_view_function(func):
    """Registers functions to be run from the update_view function"""
    func._is_registered = True
    return func

class GameInspectorView(QWidget):
    def __init__(self, game: "Game"):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.game = game

        self._registry = [
            getattr(self, name)  # bound method
            for name, attr in self.__class__.__dict__.items()
            if callable(attr) and getattr(attr, "_is_registered", False)
        ]

    def update_scope(self, scope: ScopesEnum):
        raise NotImplementedError("Subclasses must implement update_scope")

    def update_game(self, game: Game):
        self.game = game
        self.update_view()

    def update_view(self):
        for func in self._registry:
            func()