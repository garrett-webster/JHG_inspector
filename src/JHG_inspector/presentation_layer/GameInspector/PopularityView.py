from typing import Optional, override

from PyQt6.QtWidgets import QComboBox, QWidget, QVBoxLayout, QGridLayout, QLabel

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.logic_layer.gameset_tools.ToolDataClasses.GraphToolData import GraphToolData
from src.JHG_inspector.presentation_layer.GameInspector.GameInspectorView import GameInspectorView, update_view_function
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.LinePlotGraph import LinePlotGraph


def clear_table(table: QWidget):
    layout = table.layout()

    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()


class PopularityView(GameInspectorView):
    def __init__(self, scope: ScopesEnum, game: Optional[Game] = None, ):
        super().__init__(game, scope)
        self.game = game
        self.scope = scope

        self.graph_data = GraphToolData()
        self.graph = LinePlotGraph(self.graph_data)

        self.table = QWidget()
        self.table_layout = QGridLayout(self.table)

        self.layout.addWidget(self.table)
        self.layout.addWidget(self.player_selector)
        self.layout.addWidget(self.graph)

        self.update_scope(scope)

    @override
    def update_scope(self, scope: ScopesEnum):
        super().update_scope(scope)

    @override
    def update_player(self, index: int):
        super().update_player(index)
        self.update_components()

    @update_view_function
    def update_components(self):
        """Updates the data that is used to draw the graph based on the scope selected."""
        def overview_graph():
            for player in self.game.players:
                popularity = player.round_popularity
                self.graph_data.add_line(player.name, popularity)
                self.graph.update()
                self.graph.show()
                self.player_selector.hide()

        def player_graph():
            player = self.selected_player
            self.graph_data.add_line(player.name, player.round_popularity)
            self.graph.update()
            self.graph.show()
            self.player_selector.show()

            clear_table(self.table)
            self.table_layout.addWidget(QLabel("Round"), 0, 0)
            self.table_layout.addWidget(QLabel("Popularity"), 0, 1)
            for i, popularity in enumerate(player.round_popularity):
                self.table_layout.addWidget(QLabel(str(i)), i+1, 0)
                self.table_layout.addWidget(QLabel(str(round(popularity))), i+1, 1)

        def round_graph():
            self.graph.hide()
            self.player_selector.hide()

        self.graph_data.clear_lines()
        scope_to_function = {
            ScopesEnum.Overview: overview_graph,
            ScopesEnum.Player: player_graph,
            ScopesEnum.Round: round_graph,
        }

        # Run function to update data associated with the currently selected scope
        scope_to_function[self.scope]()

