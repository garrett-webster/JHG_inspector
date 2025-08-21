from typing import Optional

from PyQt6.QtWidgets import QLabel

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.presentation_layer.GameInspector.GameInspectorView import GameInspectorView
from src.JHG_inspector.presentation_layer.GameInspector.TableWidget import TableWidget
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum


class TransactionsView(GameInspectorView):
    def __init__(self, scope: ScopesEnum, game: Optional[Game] = None):
        super().__init__(game, scope)
        self.layout.addWidget(QLabel("Transactions"))

        self.table = TableWidget()

    def update_scope(self, scope: ScopesEnum):
        print(scope)

    @override
    def update_overview_components(self):
        # for round in self.game.rounds:
        print(self.game.allocations)

    @override
    def update_player_components(self):
        print("AH")

    @override
    def update_round_components(self):
        print("BHHHH")