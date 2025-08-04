from src.JHG_inspector.presentation_layer.panels.Panel import Panel
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.Component import Component


class View(Panel):
    def __init__(self, tool: "Tool"):
        name = f"{tool.name}: {tool.gameset.name}"
        super().__init__(name=name, tool=tool)
        self.components: list[Component] = []