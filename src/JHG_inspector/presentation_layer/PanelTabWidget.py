from PyQt6.QtWidgets import QTabWidget


class PanelTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)