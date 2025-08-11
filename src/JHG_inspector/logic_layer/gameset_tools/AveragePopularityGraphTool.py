from src.JHG_inspector.logic_layer.Gameset import Gameset
from src.JHG_inspector.logic_layer.gameset_tools.Tool import Tool
from src.JHG_inspector.logic_layer.gameset_tools.ToolDataClasses.GraphToolData import GraphToolData
from src.JHG_inspector.presentation_layer.panels.tool_views.OneColumnView import OneColumnView
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.LinePlotGraph import LinePlotGraph


class AveragePopularityGraphTool(Tool):
    def __init__(self, view_parent, gameset: Gameset):
        super().__init__("Average Popularity Graph", gameset, view_parent)
        self.update()

    def _update_data(self):
        self.graph_data.lines = []
        self.graph_data.num_colors_used = 0
        # Calculate the average popularity each round and construct a list of those average popularities for each game
        for game in self.games:
            line_data = []
            for round in game.rounds:
                line_data.append(sum(round.popularities) / len(round.popularities))
            self.graph_data.add_line(game.code, line_data)

    def setup_view(self):
        view = OneColumnView(self)
        self.graph_data = GraphToolData()
        self.line_plot_component = LinePlotGraph(self.graph_data)

        view.column.add_component(self.line_plot_component)

        return view

