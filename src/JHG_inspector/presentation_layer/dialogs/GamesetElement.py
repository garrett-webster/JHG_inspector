from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QFormLayout, QSizePolicy, QHBoxLayout

from src.JHG_inspector.data_layer.Gameset import Gameset


class GamesetElement(QWidget):
    def __init__(self, title: str, gameset: Gameset):
        super().__init__()

        self.toggle_button = QPushButton(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)

        self.content = GamesList(gameset)
        self.content.setVisible(False)

        self.toggle_button.clicked.connect(self.toggle_content)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content)
        self.setLayout(layout)

    def toggle_content(self):
        is_expanded = self.toggle_button.isChecked()
        self.content.setVisible(is_expanded)

    def get_smallest_width(self):
        return self.content.get_smallest_width()

class GamesList(QWidget):
    def __init__(self, gameset):
        super().__init__()
        self.buttons = []

        layout = QVBoxLayout()

        header = QHBoxLayout()
        header.addWidget(QLabel("Game Code"))
        add_game_button = QPushButton("Add Game")
        header.addWidget(add_game_button)
        layout.addLayout(header)

        game_widgets = []
        for i, game in enumerate(gameset.games.values()):
            game_widgets.append(QLabel(game.code))
            delete_button = QPushButton("Delete")
            delete_button.setSizePolicy(
                QSizePolicy.Policy.Maximum,  # no stretching horizontally
                QSizePolicy.Policy.Fixed  # no stretching vertically
            )
            self.buttons.append(delete_button)
            row = QHBoxLayout()
            row.addWidget(game_widgets[i])
            row.addWidget(delete_button)
            layout.addLayout(row)

        self.setLayout(layout)

    def get_smallest_width(self):
        if not self.buttons:
            return QSize(100, 800)  # fallback

        min_width = min(btn.sizeHint().width() for btn in self.buttons)
        # total_height = sum(btn.sizeHint().height() for btn in self.buttons)
        return QSize(min_width, 800)
        