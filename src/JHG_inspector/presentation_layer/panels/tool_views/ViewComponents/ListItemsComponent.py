from PyQt6.QtWidgets import QVBoxLayout, QLabel

from src.JHG_inspector.logic_layer.gameset_tools.ToolDataClasses.ToolData import ToolData
from src.JHG_inspector.presentation_layer.panels.tool_views.View import View
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.Component import Component


class ListItemsComponent(Component):
    def __init__(self, parent, data: ToolData, view:View):
        super().__init__(parent, data)
        self.view = view
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

    def update(self):
        # Clear the layout
        for i in reversed(range(self.layout.count())):
            widgetToRemove = self.layout.itemAt(i).widget()
            self.layout.removeWidget(widgetToRemove)
            widgetToRemove.setParent(None)

        for game in self.data.list():
            self.layout.addWidget(QLabel(game.name))