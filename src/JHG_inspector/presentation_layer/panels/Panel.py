from PyQt6.QtWidgets import QWidget


class Panel(QWidget):
    def __init__(self, parent=None, name: str = "Untitled"):
        super().__init__(parent)
        self.name = name