from typing import Optional

from PyQt6.QtWidgets import QLabel

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.presentation_layer.GameInspector.GameInspectorView import GameInspectorView
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum


class TransactionsView(GameInspectorView):
    def __init__(self, game: Optional[Game] = None):
        super().__init__(game)
        self.layout.addWidget(QLabel("Transactions"))

    def update_scope(self, scope: ScopesEnum):
        print(scope)