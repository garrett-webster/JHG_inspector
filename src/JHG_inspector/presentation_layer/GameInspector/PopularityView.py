from typing import Optional

from PyQt6.QtWidgets import QLabel

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.logic_layer.gameset_tools.ToolDataClasses.GraphToolData import GraphToolData
from src.JHG_inspector.presentation_layer.GameInspector.GameInspectorView import GameInspectorView, update_view_function
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.LinePlotGraph import LinePlotGraph

DEFAULT_SCOPE = next(iter(ScopesEnum))

class PopularityView(GameInspectorView):
    def __init__(self, game: Optional[Game] = None, scope: ScopesEnum = DEFAULT_SCOPE):
        super().__init__(game)
        self.game = game

        self.graph_data = GraphToolData()
        self.graph = LinePlotGraph(self.graph_data)

        self.scope_label = QLabel(scope.name)
        self.layout.addWidget(self.graph)

        self.update_scope(DEFAULT_SCOPE)

    @update_view_function
    def update_graph(self):
        self.graph_data.clear_lines()

        def over_view_graph():
            for player in self.game.players:
                popularity = player.round_popularity
                self.graph_data.add_line(player.name, popularity)

        over_view_graph()
        self.graph.update()

    def update_code(self, code:str):
        self.game_code_label.setText(code)


    def update_scope(self, scope:str):
        if self.game:
            self.update_graph(ScopesEnum(scope))