from typing import override

from PyQt6.QtWidgets import QLabel

from src.JHG_inspector.presentation_layer.GameInspector.GameInspectorView import GameInspectorView
from src.JHG_inspector.presentation_layer.GameInspector.TableWidget import TableWidget
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum


class TransactionsView(GameInspectorView):
    def __init__(self, game_inspector: "GameInspector"):
        super().__init__(game_inspector)
        self.game_inspector = game_inspector
        self.layout.addWidget(QLabel("Transactions"))

        self.table = TableWidget()

        self.update_components()

    def update_scope(self, scope: ScopesEnum):
        print(scope)

    @override
    def update_overview_components(self):
        print(self.game_inspector.selected_game.get_allocations_sum_matrix)

    @override
    def update_player_components(self):
        print("AH")

    @override
    def update_round_components(self):
        print("BHHHH")