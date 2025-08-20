from typing import Optional, override

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QHBoxLayout, QSizePolicy, QStackedWidget

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.logic_layer.gameset_tools.ToolDataClasses.GraphToolData import GraphToolData
from src.JHG_inspector.presentation_layer.GameInspector.GameInspectorView import GameInspectorView, update_view_function
from src.JHG_inspector.presentation_layer.GameInspector.TableWidget import TableWidget
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.BarGraph import BarGraph
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.LinePlotGraph import LinePlotGraph



class PopularityView(GameInspectorView):
    def __init__(self, scope: ScopesEnum, game: Optional[Game] = None, ):
        super().__init__(game, scope)
        self.game = game
        self.scope = scope

        self.graph_data = GraphToolData()
        self.line_graph = LinePlotGraph(self.graph_data)
        self.bar_graph = BarGraph(self.graph_data)
        self.graph = QStackedWidget(self)
        self.graph.addWidget(self.line_graph)
        self.graph.addWidget(self.bar_graph)
        self.graph.setCurrentWidget(self.line_graph)

        self.table = TableWidget()
        self.table.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        self.table_graph_layout = QHBoxLayout()
        self.table_graph_layout.addWidget(self.table, alignment=Qt.AlignmentFlag.AlignTop)
        self.table_graph_layout.addWidget(self.graph)

        self.layout.addWidget(self.player_selector, alignment=Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.round_selector, alignment=Qt.AlignmentFlag.AlignTop)
        self.layout.addLayout(self.table_graph_layout)

        self.update_scope(scope)

    @update_view_function
    def update_components(self):
        """Updates the data that is used to draw the graph based on the scope selected."""

        self.table.hide()
        self.player_selector.hide()
        self.round_selector.hide()

        def overview_components():
            self.graph.setCurrentWidget(self.line_graph)
            for player in self.game.players:
                popularity = player.round_popularity
                self.graph_data.add_entry(player.name, popularity)
            self.line_graph.update()

        def player_components():
            self.graph.setCurrentWidget(self.line_graph)
            player = self.selected_player
            self.graph_data.add_entry(player.name, player.round_popularity)
            self.line_graph.update()

            self.table.clear()
            self.table.table_layout.addWidget(QLabel("Round"), 0, 0)
            self.table.table_layout.addWidget(QLabel("Popularity"), 0, 1)
            for i, popularity in enumerate(player.round_popularity):
                self.table.table_layout.addWidget(QLabel(str(i+1)), i+1, 0)
                self.table.table_layout.addWidget(QLabel(str(round(popularity))), i+1, 1)

            self.table.show()
            self.line_graph.show()
            self.player_selector.show()

        def round_components():
            self.round_selector.show()
            self.graph.setCurrentWidget(self.bar_graph)

            for player in self.game.players:
                self.graph_data.add_entry(player.name, player.round_popularity)
            self.bar_graph.update(self.selected_round.round_number)


        self.graph_data.clear_entries()
        scope_to_function = {
            ScopesEnum.Overview: overview_components,
            ScopesEnum.Player: player_components,
            ScopesEnum.Round: round_components,
        }

        # Run function to update data associated with the currently selected scope
        scope_to_function[self.scope]()

