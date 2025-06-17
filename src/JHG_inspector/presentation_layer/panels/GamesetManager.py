from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QSizePolicy

from src.JHG_inspector.data_layer.Gameset import Gameset
from src.JHG_inspector.presentation_layer.dialogs.GamesetElement import GamesetElement
from src.JHG_inspector.presentation_layer.panels.Panel import Panel


class GamesetManager(Panel):
    def __init__(self, database):
        super().__init__()
        self.gameset_elements = []

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(content_widget)

        wrapper_layout = QVBoxLayout(self)
        wrapper_layout.addWidget(scroll_area)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        for gameset in database.gamesets.values():
            self.add_gameset(gameset.name, gameset)

    def add_gameset(self, title: str, gameset: Gameset):
        section = GamesetElement(title, gameset)
        section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.layout.addWidget(section)


    def sizeHint(self):
        if not self.gameset_elements:
            return QSize(100, 800)
        # min_width = self.gameset_elements[0].sizeHint().width()
        min_width = min(element.sizeHint().width for element in self.gameset_elements)
        # for gameset_element in self.gameset_elements:
        #     if gameset_element.sizeHint().width() < min_width:
        #         sum(btn.sizeHint().height() for btn in self.buttons)

        return QSize(min_width, 800)