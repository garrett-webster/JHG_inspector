from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QComboBox, QWidget, QVBoxLayout, QListView, QStackedWidget, QFrame, QLabel

from src.JHG_inspector.logic_layer.Game import Game
from src.JHG_inspector.presentation_layer.GameInspector.PopularityView import PopularityView
from src.JHG_inspector.presentation_layer.GameInspector.TransactionsView import TransactionsView
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum, ViewEnum
from src.JHG_inspector.presentation_layer.panels.Panel import Panel

DEFAULT_SCOPE: ScopesEnum = next(iter(ScopesEnum))

class GameInspectorPanel(Panel):
    def __init__(self, game_inspector: "GameInspector", games: list["Game"], parent=None):
        """Params:
             game_inspector:
               GameInspector instance being displayed
             games: list[Game]
               list of games that can be inspected (may be all loaded games, or may just be the games in a particular gameset)
               """

        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.game_inspector = game_inspector
        self.games = games

        self.selected_game: Optional[Game] = games[0]
        self.selected_scope: Optional[ScopesEnum] = None
        self.selected_view: Optional[ViewEnum] = None

        # Set up the view, which changes what is shown based on the selected scope and view
        self.view = QStackedWidget()
        self.views = {
            ViewEnum.Popularity: PopularityView(DEFAULT_SCOPE, self.selected_game),
            ViewEnum.Transactions: TransactionsView(DEFAULT_SCOPE, self.selected_game),
        }

        for view in self.views.values():
            self.view.addWidget(view)

        self.game_label = QLabel("Game:")

        # Dropdown box for selecting the game
        # TODO: Change this to a button that brings up a modal or something
        game_selector = QComboBox()
        for game in games:
            game_selector.addItem(game.code)
        game_selector.currentIndexChanged.connect(self.update_game)

        game_selection_layout = QHBoxLayout()
        game_selection_layout.addWidget(self.game_label)
        game_selection_layout.addWidget(game_selector)

        # Dropdown box for selecting the scope
        scope_selector = QComboBox()
        scope_selector.setView(QListView())
        for scope in ScopesEnum:
            scope_selector.addItem(scope.name)
        scope_selector.currentTextChanged.connect(self.update_scope)

        # Dropdown box for selecting which data view is displayed
        view_selector = QComboBox()
        for page in ViewEnum:
            view_selector.addItem(page.name)
        view_selector.currentTextChanged.connect(self.update_view)

        divider_line = QFrame()
        divider_line.setObjectName('divider_line')
        divider_line.setFrameShape(QFrame.Shape.HLine)
        divider_line.setFrameShadow(QFrame.Shadow.Sunken)

        scope_view_selection_layout = QHBoxLayout()
        scope_view_selection_layout.addWidget(scope_selector)
        scope_view_selection_layout.addWidget(view_selector)

        # Add everything to the GUI
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.addLayout(game_selection_layout)
        header_layout.addLayout(scope_view_selection_layout)

        self.layout.addWidget(header)
        self.layout.addWidget(divider_line)
        self.layout.addWidget(self.view)

    def update_game(self, index: int):
        self.selected_game = self.games[index]
        self.view.currentWidget().update_game(self.selected_game)

    def update_scope(self, scope:str):
        scope = ScopesEnum(scope)
        self.selected_scope = scope
        self.game_inspector.scope = scope
        self.view.currentWidget().update_scope(scope)

    def update_view(self, view: str):
        self.selected_view = ViewEnum(view)
        self.view.setCurrentWidget(self.views[self.selected_view])
        self.view.currentWidget().update_components()

    # TODO: Figure out if I even want this functionality
    def update_games(self, games: list["Game"]):
        self.games = games
