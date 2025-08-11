from src.JHG_inspector.logic_layer.Gameset import Gameset

from src.JHG_inspector.logic_layer.gameset_tools.GamesListTool import GamesListTool
from src.JHG_inspector.logic_layer.gameset_tools.AveragePopularityTool import AveragePopularityTool
from src.JHG_inspector.logic_layer.gameset_tools.AveragePopularityGraphTool import AveragePopularityGraphTool


class ToolsManager:
    def __init__(self):
        from src.JHG_inspector.logic_layer.gameset_tools.Tool import Tool

        self.tools_types_list = Tool.tool_types_list
        self.gameset_to_tools = {}

    def new_tool(self, view_parent, tool_type, gameset: Gameset):
        if tool_type in self.tools_types_list:
            new_tool = tool_type(view_parent, gameset)
            self.gameset_to_tools[gameset.id].add(new_tool)

            return new_tool
        else:
            raise ValueError(f"No tool of type {tool_type}")

    def new_gameset(self, gameset: Gameset):
        self.gameset_to_tools[gameset.id] = set()

    def update_tools(self, gameset_id: int):
        if gameset_id in self.gameset_to_tools:
            for tool in self.gameset_to_tools[gameset_id]:
                tool.update()
