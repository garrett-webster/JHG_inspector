from PyQt6.QtWidgets import QVBoxLayout

from src.JHG_inspector.presentation_layer.panels.tool_views.View import View
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.Component import Component


class OneColumnView(View):
    def __init__(self, parent):
        super().__init__()
        self.column = Column(self)

class Column(QVBoxLayout):
    def __init__(self, parent:View):
        super().__init__(parent)
        self.view = parent

    def add_component(self, component: Component):
        self.view.components.append(component)
        self.addWidget(component)