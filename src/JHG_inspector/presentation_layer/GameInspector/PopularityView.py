from typing import Optional

from PyQt6.QtWidgets import QLabel

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.presentation_layer.GameInspector.GameInspectorView import GameInspectorView
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum

DEFAULT_SCOPE = next(iter(ScopesEnum))

class PopularityView(GameInspectorView):
    def __init__(self, game: Optional[Game] = None, scope: ScopesEnum = DEFAULT_SCOPE):
        super().__init__(game)

        if game:
            self.game_code_label = QLabel(game.code)
        else:
            self.game_code_label = QLabel('No game selected')

        self.scope_label = QLabel(scope.name)
        self.layout.addWidget(self.game_code_label)
        self.layout.addWidget(self.scope_label)

    def update_code(self, code:str):
        self.game_code_label.setText(code)

    def update_scope(self, scope:str):
        self.scope_label.setText(scope)