from typing import Optional

from PyQt6.QtWidgets import QLabel

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.logic_layer.gameset_tools.ToolDataClasses.GraphToolData import GraphToolData
from src.JHG_inspector.presentation_layer.GameInspector.GameInspectorView import GameInspectorView, update_view_function
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.LinePlotGraph import LinePlotGraph

class PopularityView(GameInspectorView):
    def __init__(self, scope: ScopesEnum, game: Optional[Game] = None, ):
        super().__init__(game, scope)
        self.game = game
        self.scope = scope

        self.graph_data = GraphToolData()
        self.graph = LinePlotGraph(self.graph_data)

        self.scope_label = QLabel(scope.name)
        self.layout.addWidget(self.graph)

        self.update_scope(scope)

    @update_view_function
    def update_graph(self):
        def over_view_graph():
            for player in self.game.players:
                popularity = player.round_popularity
                self.graph_data.add_line(player.name, popularity)

        scope_to_function = {
            ScopesEnum.Overview: over_view_graph,
        }
        self.graph_data.clear_lines()

        over_view_graph()
        self.graph.update()