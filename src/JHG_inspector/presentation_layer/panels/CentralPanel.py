from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QStackedLayout, QLabel, QVBoxLayout, QPushButton

from src.JHG_inspector.presentation_layer.Container import Container


class CentralPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.num_containers = 0
        self.stack = QStackedLayout()
        self.setLayout(self.stack)

        self.fallback = QWidget()
        fallback_layout = QVBoxLayout()
        fallback_label = QLabel("No panels open.")
        fallback_open_button = QPushButton("Open New Panel")
        fallback_open_button.clicked.connect(self.open_panel)
        fallback_layout.addStretch()
        fallback_layout.addWidget(fallback_label, alignment=Qt.AlignmentFlag.AlignCenter)
        fallback_layout.addWidget(fallback_open_button, alignment=Qt.AlignmentFlag.AlignCenter)
        fallback_layout.addStretch()
        self.fallback.setLayout(fallback_layout)

        self.container = Container(self.update_view)

        self.stack.addWidget(self.container)  # Index 0
        self.stack.addWidget(self.fallback)   # Index 1

        self.stack.setCurrentWidget(self.container)

    def update_view(self):
        if Container.num_containers == 0:
            self.stack.setCurrentWidget(self.fallback)
        else:
            self.stack.setCurrentWidget(self.container)

    def open_panel(self):
        self.container = Container(self.update_view)
        self.stack.addWidget(self.container)
        self.stack.setCurrentWidget(self.container)