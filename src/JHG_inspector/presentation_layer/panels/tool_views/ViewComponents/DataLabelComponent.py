from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel

from src.JHG_inspector.logic_layer.tools.ToolDataClasses.DataLabelToolData import DataLabelToolData
from src.JHG_inspector.presentation_layer.panels.tool_views.View import View
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.Component import Component


class DataLabelComponent(Component):
    def __init__(self, parent, data: DataLabelToolData, view: View):
        super().__init__(parent, data)
        self.view = view
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.data_name = data.name

        self.data_title = QLabel(f"{self.data_name}: ")
        self.data_label = QLabel()
        self.layout.addWidget(self.data_title)
        self.layout.addWidget(self.data_label)

        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        if data is not None:
            self.data_label.setText(data.to_str)

    def update(self):
        self.data_title.setText(f"{self.data.name}: ")
        self.data_label.setText(self.data.to_str)