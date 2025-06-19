from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QWidget, QSizePolicy

from src.JHG_inspector.data_layer.Gameset import Gameset
from src.JHG_inspector.presentation_layer.components.GamesetElement import GamesetElement


class GamesetsDialog(QDialog):
    def __init__(self, database):
        super().__init__()
        self.setMinimumSize(400, 300)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(content_widget)

        wrapper_layout = QVBoxLayout(self)
        wrapper_layout.addWidget(scroll_area)

        for gameset in database.gamesets.values():
            self.add_gameset(gameset.name, gameset)

    def add_gameset(self, title: str, gameset: Gameset):
        section = GamesetElement(title, gameset)
        section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.layout.addWidget(section)
