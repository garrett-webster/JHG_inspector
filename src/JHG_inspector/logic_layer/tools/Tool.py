from abc import ABC, abstractmethod

from src.JHG_inspector.data_layer.Gameset import Gameset
from src.JHG_inspector.presentation_layer.panels.tool_views.View import View
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.Component import Component


class Tool(ABC):
    tool_types_list = []
    """Abstract class used as a base class to create tools.

       Provides the basic functionality that a tool needs to be easily created.
       """

    def __init__(self, gameset: Gameset):
        self.gameset = gameset
        self.view = view
        self.components: list[Component] = []

        self.view = self.setup_view()

    def __init_subclass__(cls):
        Tool.tool_types_list.append(cls)

    def update(self):
        """A call back given to the ToolsManager that updates the ToolData objects and their associated Components."""
        self._update_data()
        self._update_components()

    @abstractmethod
    def _update_data(self):
        ...

    def _update_components(self):
        """Calls the update method on each component.

           Iterates through the components and displays the current values of their ToolData objects."""
        for component in self.components:
            component.update()

    @abstractmethod
    def _update_data(self):
        """Uses the gameset to update the ToolData objects.

           When creating a new Tool, this method is where the bulk of the work is done. The Tool creator will manipulate
           the data from the gameset to produce the results they want, then assign those values to the appropriate
           ToolData objects."""
        ...

    @abstractmethod
    def setup_view(self) -> View:
        """Sets up the view.

           When creating a new Tool, the components will be created and assigned to the view here. setup_view is
           automatically called when creating a new Tool."""
        ...