from typing import override

from PyQt6.QtWidgets import QLabel

from src.JHG_inspector.logic_layer.tools.ToolDataClasses.ToolData import ToolData
from src.JHG_inspector.logic_layer.tools.Tool import Tool
from src.JHG_inspector.presentation_layer.panels.tool_views.OneColumnView import OneColumnView


class GamesListTool(Tool):
    def __init__(self, view_parent, gameset: "Gameset"):
        super().__init__("Games List", gameset, view_parent)
        self.num_games = ToolData()

        self.update()

    def _update_data(self):
        self.game_codes = []
        for game in self.gameset.games.values():
            self.game_codes.append(game.code)

    @override
    def _update_components(self):
        self.clearLayout()
        for game_name in self.game_codes:
            self.view.column.addWidget(QLabel(game_name))

    def setup_view(self):
        view = OneColumnView(self.view_parent)

        return view

    def clearLayout(self):
        while self.view.column.count():
            child = self.view.column.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
