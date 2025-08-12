from typing import Optional

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.presentation_layer.GameInspector.GameInspectorPanel import GameInspectorPanel
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum, ToolPageEnum


class GameInspector:
    def __init__(self, game: Optional[Game] = None):
        self.game: Game = game
        self.scope_selected: ScopesEnum
        self.info_selected: ToolPageEnum
        self.panel = GameInspectorPanel(self)

