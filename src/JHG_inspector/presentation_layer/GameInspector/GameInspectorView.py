from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.logic_layer.Player import Player
from src.JHG_inspector.logic_layer.Round import Round
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum


def hide_components(*components: QWidget):
    for component in components:
        component.hide()

def show_components(*components: QWidget):
    for component in components:
        component.show()


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

        self.layout.addWidget(self.player_selector, alignment=Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.round_selector, alignment=Qt.AlignmentFlag.AlignTop)

    def update_scope(self, scope: ScopesEnum):
        self.scope = scope
        self.update_components()

    def update_game(self, game: Game):
        self.game = game

        self.player_selector.clear()
        for player in self.game.players:
            self.player_selector.addItem(player.name)

        self.update_components()

    def update_player(self, index: int):
        self.selected_player = self.game.players[index]
        self.update_components()

    def update_round(self, index: int):
        self.selected_round = self.game.rounds[index]
        self.update_components()

    def update_overview_components(self):
        raise NotImplementedError(f"update_overview_components not implemented for {self.__class__.__name__}")

    def update_player_components(self):
        raise NotImplementedError(f"update_player_components not implemented for {self.__class__.__name__}")

    def update_round_components(self):
        raise NotImplementedError(f"update_round_components not implemented for {self.__class__.__name__}")

    def update_components(self):
        scope_to_function = {
            ScopesEnum.Overview: self.update_overview_components,
            ScopesEnum.Player: self.update_player_components,
            ScopesEnum.Round: self.update_round_components,
        }

        # Run function to update data associated with the currently selected scope
        scope_to_function[self.scope]()

