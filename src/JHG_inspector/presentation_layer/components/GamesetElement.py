from functools import partial

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QSizePolicy, QMessageBox, QMenu

from src.JHG_inspector.logic_layer.Gameset import Gameset
from src.JHG_inspector.presentation_layer.components.GamesList import GamesList


class GamesetElement(QWidget):
    class ToggleBanner(QPushButton):
        def __init__(self, title, gameset_element):
            super().__init__(title)
            self.setCheckable(True)
            self.setChecked(False)
            self.clicked.connect(gameset_element.toggle_content)

            self.setProperty("class", "GamesetElementBanner")
            self.style().unpolish(self)
            self.style().polish(self)
            self.setMinimumWidth(0)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def __init__(self, title: str, gameset: Gameset, select_game, remove_game, remove_gameset):
        super().__init__()
        self.gameset = gameset
        self.remove_gameset = remove_gameset
        self.select_game = select_game

        self.toggle_banner = self.ToggleBanner(title, self)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete)

        self.content = GamesList(gameset, delete_button, select_game, remove_game)
        self.content.setVisible(False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toggle_banner)
        layout.addWidget(self.content)
        self.setLayout(layout)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

    def open_context_menu(self, pos: QPoint):
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete)

        manage_games_action = QAction("Manage Games", self)
        manage_games_action.triggered.connect(partial(self.select_game, self.gameset))

        menu = QMenu(self)
        menu.addAction(delete_action)
        menu.addAction(manage_games_action)
        menu.exec(self.mapToGlobal(pos))

    def toggle_content(self):
        is_expanded = self.toggle_banner.isChecked()
        self.content.setVisible(is_expanded)

    def delete(self):
        result = QMessageBox.question(
            self,
            "Delete Gameset",
            "Are you sure you want to delete this gameset?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if result == QMessageBox.StandardButton.Yes:
            self.remove_gameset(self.gameset)