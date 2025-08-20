from PyQt6.QtWidgets import QGridLayout, QWidget


class TableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table_layout = QGridLayout(self)
        self.setLayout(self.table_layout)

    def clear(self):
        while self.table_layout.count():
            item = self.table_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()