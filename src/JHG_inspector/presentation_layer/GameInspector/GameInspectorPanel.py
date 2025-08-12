from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QComboBox, QWidget, QVBoxLayout, QListView

from src.JHG_inspector.presentation_layer.GameInspector.PopularityView import PopularityView
from src.JHG_inspector.presentation_layer.GameInspector.game_inspector_enums import ScopesEnum, ToolPageEnum
from src.JHG_inspector.presentation_layer.panels.Panel import Panel


class GameInspectorPanel(Panel):
    def __init__(self, game_inspector: "GameInspector", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # TO BE DELETED LATER
        self.view = PopularityView(game_inspector.game)

        scope_selector = QComboBox()
        scope_selector.setView(QListView())
        for scope in ScopesEnum:
            scope_selector.addItem(scope.name)
        scope_selector.currentTextChanged.connect(self.update_scope)

        page_selector = QComboBox()
        for page in ToolPageEnum:
            page_selector.addItem(page.name)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.addWidget(scope_selector)
        header_layout.addWidget(page_selector)

        self.layout.addWidget(header)
        self.layout.addWidget(self.view)

    def update_scope(self, scope:str):
        print(scope)
        self.view.update_scope(scope)
