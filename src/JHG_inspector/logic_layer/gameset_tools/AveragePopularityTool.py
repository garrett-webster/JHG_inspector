import math
import statistics

from src.JHG_inspector.logic_layer.gameset_tools.ToolDataClasses.DataLabelToolData import DataLabelToolData
from src.JHG_inspector.logic_layer.gameset_tools.ToolDataClasses.ToolData import ToolData
from src.JHG_inspector.logic_layer.gameset_tools.Tool import Tool
from src.JHG_inspector.presentation_layer.panels.tool_views.OneColumnView import OneColumnView
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.DataLabelComponent import DataLabelComponent


class AveragePopularityTool(Tool):
    def __init__(self, view_parent, gameset: "Gameset"):
        super().__init__("Average Popularity", gameset, view_parent)
        self.update()

    def _update_data(self):
        end_popularitites = []

        for game in self.games:
            end_popularitites.append(statistics.fmean(game.popularities[-1]))

        if end_popularitites:
            non_truncated_average = statistics.fmean(end_popularitites)
            self.data_label_data.raw = math.trunc(non_truncated_average * 100) / 100 # Truncates to two decimal places
        else:
            self.data_label_data.raw = None

    def setup_view(self):
        view = OneColumnView(self)
        self.data_label_data = DataLabelToolData("Average Popularity")
        self.average_popularity_component = DataLabelComponent(self.view_parent, self.data_label_data, view)

        view.column.add_component(self.average_popularity_component)

        return view