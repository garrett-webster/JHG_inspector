from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QWidget, QLabel, QVBoxLayout


class TableWidget(QWidget):
    def __init__(self, parent=None, description: str = None, outer_border: bool = False):
        super().__init__(parent)
        self.setObjectName("TableWidget")

        with open("src/JHG_inspector/presentation_layer/stylesheets/Table.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.description = QLabel()
        self.description.setWordWrap(True)
        self.description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if description:
            self.description.setText(description)

        self.table_body = QWidget()
        self.table_body.setObjectName("table_body")
        self.table_body.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.table_layout = QGridLayout(self.table_body)

        if outer_border:
            self.table_layout.setContentsMargins(3, 3, 3, 3)
        else:
            self.table_layout.setContentsMargins(0, 0, 0, 0)

        self.table_layout.setSpacing(3)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(25)
        self.layout.addWidget(self.description)
        self.layout.addWidget(self.table_body)

    def clear(self):
        while self.table_layout.count():
            item = self.table_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def add_widget(self, widget: QWidget, row_num: int, col_num: int):
        self.table_layout.addWidget(widget, row_num, col_num)