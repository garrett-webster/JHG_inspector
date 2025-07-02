from abc import ABC, abstractmethod

from src.JHG_inspector.data_layer.Gameset import Gameset
from src.JHG_inspector.presentation_layer.panels.tool_views.View import View
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.Component import Component


class Tool(ABC):
    def __init__(self, gameset: Gameset, view: View):
        self.gameset = gameset
        self.view = view
        self.components: list[Component] = []

    def update(self):
        """A call back given to the ToolsManager that updates the ToolData objects and their associated Components."""
        self._update_data()
        self._update_components()

    @abstractmethod
    def _update_data(self):
        ...

    def _update_components(self):
        for component in self.components:
            component.update()