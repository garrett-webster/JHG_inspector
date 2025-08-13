from typing import Optional

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.presentation_layer.GameInspector.GameInspectorPanel import GameInspectorPanel
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum, ViewEnum


class GameInspector:
    def __init__(self, games: list["Game"], game: Optional[Game] = None, gameset: Optional["Gameset"] = None):
        self.game: Game = game
        self.scope_selected: ScopesEnum
        self.view_selected: ViewEnum
        # TODO: Sort the games if a gameset has been passed, such that the panel only has access to the games in the
        #  current gameset

        self.panel = GameInspectorPanel(self, games)

