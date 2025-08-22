from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum


def hide_components(*components: QWidget):
    for component in components:
        component.hide()

def show_components(*components: QWidget):
    for component in components:
        component.show()


class GameInspectorView(QWidget):
    def __init__(self, game_inspector: "GameInspector"):
        super().__init__()
        self._suppress_updates = False
        self.game_inspector = game_inspector
        self.layout = QVBoxLayout(self)

        self.player_selector = QComboBox()
        for player in self.game_inspector.selected_game.players:
            self.player_selector.addItem(player.name)
        self.player_selector.currentIndexChanged.connect(self.update_player)
        self.player_selector.hide()

        self.round_selector = QComboBox()
        self.round_selector.hide()
        self.populate_round_selector()

        self.layout.addWidget(self.player_selector, alignment=Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.round_selector, alignment=Qt.AlignmentFlag.AlignTop)

    def update_scope(self, scope: ScopesEnum):
        self.game_inspector.selected_scope = scope
        self.update_components()

    def update_game(self, game: Game):
        self._suppress_updates = True
        try:
            self.game_inspector.selected_game = game

            self.player_selector.clear()
            for player in self.game_inspector.selected_game.players:
                self.player_selector.addItem(player.name)

            self.populate_round_selector()
        finally:
            self._suppress_updates = False
        self.update_components()

    def update_player(self, index: int):
        self.game_inspector.selected_player = self.game_inspector.selected_game.players[index]
        self.update_components()

    def update_round(self, index: int):
        self.game_inspector.selected_round = self.game_inspector.selected_game.rounds[index]
        self.update_components()

    def update_overview_components(self):
        raise NotImplementedError(f"update_overview_components not implemented for {self.__class__.__name__}")

    def update_player_components(self):
        raise NotImplementedError(f"update_player_components not implemented for {self.__class__.__name__}")

    def update_round_components(self):
        raise NotImplementedError(f"update_round_components not implemented for {self.__class__.__name__}")

    def update_components(self):
        if self._suppress_updates:
            return

        scope_to_function = {
            ScopesEnum.Overview: self.update_overview_components,
            ScopesEnum.Player: self.update_player_components,
            ScopesEnum.Round: self.update_round_components,
        }

        # Run function to update data associated with the currently selected scope
        scope_to_function[self.game_inspector.selected_scope]()

    def populate_round_selector(self):
        self.round_selector.blockSignals(True)
        try:
            self.round_selector.clear()
            for round in self.game_inspector.selected_game.rounds:
                self.round_selector.addItem(f"Round {round.round_number + 1}")

            if self.game_inspector.selected_round.round_number > (len(self.game_inspector.selected_game.rounds) - 1):
                self.round_selector.setCurrentIndex(0)
                self.game_inspector.selected_round = self.game_inspector.selected_game.rounds[0]
        finally:
            self.round_selector.blockSignals(False)
