from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QSizePolicy, QMessageBox

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

    def toggle_content(self):
        is_expanded = self.toggle_banner.isChecked()
        self.content.setVisible(is_expanded)

    def get_smallest_width(self):
        return self.content.get_smallest_width()

    def delete(self):
        result = QMessageBox.question(
            self,
            "Delete Gameset",
            "Are you sure you want to delete this gameset?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if result == QMessageBox.StandardButton.Yes:
            self.remove_gameset(self.gameset)