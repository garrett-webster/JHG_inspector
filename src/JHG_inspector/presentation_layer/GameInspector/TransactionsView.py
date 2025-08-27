from typing import override

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

from src.JHG_inspector.presentation_layer.GameInspector.GameInspectorView import GameInspectorView
from src.JHG_inspector.presentation_layer.GameInspector.TableWidget import TableWidget


class TransactionsView(GameInspectorView):
    def __init__(self, game_inspector: "GameInspector"):
        super().__init__(game_inspector)
        self.game_inspector = game_inspector

        self.table = TableWidget(description="Shows the sum of all token allocations from the player listed in the corresponding row to the player in the corresponding column")

        self.layout.addWidget(self.table, alignment=Qt.AlignmentFlag.AlignTop)

        self.update_components()

    @override
    def update_overview_components(self):
        game = self.game_inspector.selected_game
        self.table.clear()

        placeholder_0_0 = QLabel("")
        placeholder_0_0.setProperty("class", "colRowHeader")
        self.table.add_widget(placeholder_0_0, 0, 0)
        for i, player_from_row in enumerate(game.get_allocations_sum_matrix):
            row_label = QLabel(str(game.id_to_name[game.player_order_to_id[i]]))
            row_label.setProperty("class", "colRowHeader")
            col_label = QLabel(str(game.id_to_name[game.player_order_to_id[i]]))
            col_label.setProperty("class", "colRowHeader")

            self.table.add_widget(row_label, i+1, 0)
            self.table.add_widget(col_label, 0, i+1)
            for j, transactions_sum in enumerate(player_from_row):
                self.table.add_widget(QLabel(str(transactions_sum)), i+1, j+1)


    @override
    def update_player_components(self):
        print("AH")

    @override
    def update_round_components(self):
        print("BHHHH")