from src.JHG_inspector.presentation_layer.panels.Panel import Panel
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.Component import Component


class View(Panel):
    def __init__(self):
        super().__init__()
        self.components: list[Component] = []