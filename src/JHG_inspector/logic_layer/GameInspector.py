from typing import Optional

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.logic_layer.Player import Player
from src.JHG_inspector.logic_layer.Round import Round
from src.JHG_inspector.presentation_layer.GameInspector.GameInspectorPanel import GameInspectorPanel
from src.JHG_inspector.presentation_layer.GameInspector.PopularityView import PopularityView
from src.JHG_inspector.presentation_layer.GameInspector.TransactionsView import TransactionsView
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum, ViewEnum


class GameInspector:
    def __init__(self, games: list["Game"], game: Optional[Game] = None, gameset: Optional["Gameset"] = None):

        self.games: list["Game"] = games

        self.selected_game: Game = game
        if not self.selected_game:
            self.selected_game = games[0]

        self.selected_round: Round = self.selected_game.rounds[0]
        self.selected_player: Player = self.selected_game.players[0]
        # TODO: Sort the games if a gameset has been passed, such that the panel only has access to the games in the
        #  current gameset

        self.selected_scope: ScopesEnum = next(iter(ScopesEnum))

        self.views = {
            ViewEnum.Popularity: PopularityView(self),
            ViewEnum.Transactions: TransactionsView(self),
        }

        self.panel = GameInspectorPanel(self)

        self.selected_view: ViewEnum = next(iter(self.views))