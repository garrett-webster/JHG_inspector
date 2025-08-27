from typing import override

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QStackedWidget

from src.JHG_inspector.logic_layer.gameset_tools.ToolDataClasses.GraphToolData import GraphToolData
from src.JHG_inspector.presentation_layer.GameInspector.GameInspectorView import (GameInspectorView, show_components,
                                                                                  hide_components)
from src.JHG_inspector.presentation_layer.GameInspector.TableWidget import TableWidget
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.BarGraph import BarGraph
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.LinePlotGraph import LinePlotGraph



class PopularityView(GameInspectorView):
    def __init__(self, game_inspector: "GameInspector"):
        super().__init__(game_inspector)

        self.graph_data = GraphToolData()
        self.line_graph = LinePlotGraph(self.graph_data)
        self.bar_graph = BarGraph(self.graph_data)
        self.graph = QStackedWidget(self)
        self.graph.addWidget(self.line_graph)
        self.graph.addWidget(self.bar_graph)
        self.graph.setCurrentWidget(self.line_graph)

        self.table = TableWidget()

        self.table_graph_layout = QHBoxLayout()
        self.table_graph_layout.addWidget(self.table, alignment=Qt.AlignmentFlag.AlignTop)
        self.table_graph_layout.addWidget(self.graph)

        self.layout.addLayout(self.table_graph_layout)

        self.update_components()

    @override
    def update_overview_components(self):
        hide_components(self.table, self.player_selector, self.round_selector)
        self.graph_data.clear_entries()
        self.graph.setCurrentWidget(self.line_graph)
        for player in self.game_inspector.selected_game.players:
            popularity = player.round_popularity
            self.graph_data.add_entry(player.name, popularity)
        self.line_graph.update()

    @override
    def update_player_components(self):
        hide_components(self.table, self.round_selector)
        self.graph_data.clear_entries()
        self.graph.setCurrentWidget(self.line_graph)
        player = self.game_inspector.selected_player
        self.graph_data.add_entry(player.name, player.round_popularity)
        self.line_graph.update()

        self.table.clear()
        self.table.table_layout.addWidget(QLabel("Round"), 0, 0)
        self.table.table_layout.addWidget(QLabel("Popularity"), 0, 1)
        for i, popularity in enumerate(player.round_popularity):
            self.table.table_layout.addWidget(QLabel(str(i+1)), i+1, 0)
            self.table.table_layout.addWidget(QLabel(str(round(popularity))), i+1, 1)

        show_components(self.table, self.player_selector)

    @override
    def update_round_components(self):
        hide_components(self.table, self.player_selector)
        self.graph_data.clear_entries()
        self.graph.setCurrentWidget(self.bar_graph)

        for player in self.game_inspector.selected_game.players:
            self.graph_data.add_entry(player.name, player.round_popularity)
        self.bar_graph.update(self.game_inspector.selected_round.round_number)

        show_components(self.round_selector)