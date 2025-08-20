from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.logic_layer.Player import Player
from src.JHG_inspector.logic_layer.Round import Round
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum

def update_view_function(func):
    """Registers functions to be run from the update_view function"""
    func._is_registered = True
    return func

class GameInspectorView(QWidget):
    def __init__(self, game: "Game", scope: ScopesEnum):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.game = game
        self.scope = scope
        self.selected_player: Player = game.players[0]
        self.selected_round: Round = game.rounds[0]

        self.player_selector = QComboBox()
        for player in self.game.players:
            self.player_selector.addItem(player.name)
        self.player_selector.currentIndexChanged.connect(self.update_player)
        self.player_selector.hide()

        self.round_selector = QComboBox()
        for round in self.game.rounds:
            self.round_selector.addItem(f"Round {round.round_number + 1}")
        self.round_selector.currentIndexChanged.connect(self.update_round)
        self.round_selector.hide()

        self._registry = [
            getattr(self, name)  # bound method
            for name, attr in self.__class__.__dict__.items()
            if callable(attr) and getattr(attr, "_is_registered", False)
        ]

    def update_scope(self, scope: ScopesEnum):
        self.scope = scope
        self.update_view()

    def update_game(self, game: Game):
        self.game = game

        self.player_selector.clear()
        for player in self.game.players:
            self.player_selector.addItem(player.name)

        self.update_view()

    def update_view(self):
        for func in self._registry:
            func()

    def update_player(self, index: int):
        self.selected_player = self.game.players[index]
        self.update_view()

    def update_round(self, index: int):
        self.selected_round = self.game.rounds[index]
        self.update_view()