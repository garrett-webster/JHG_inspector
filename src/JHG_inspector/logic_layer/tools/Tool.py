import re
from abc import ABC, abstractmethod

from src.JHG_inspector.logic_layer.Gameset import Gameset
from src.JHG_inspector.presentation_layer.panels.tool_views import View
from src.JHG_inspector.presentation_layer.panels.tool_views.ViewComponents.Component import Component


class Tool(ABC):
    tool_types_list = []
    """Abstract class used as a base class to create tools.

       Provides the basic functionality that a tool needs to be easily created.
       """

    def __init__(self, name: str, gameset: Gameset, view_parent):
        self.name = name
        self.gameset = gameset
        self.games = self.gameset.games.values()
        self.view_parent = view_parent
        self.components: list[Component] = []

        self.view = self.setup_view()

    def __init_subclass__(cls):
        Tool.tool_types_list.append(cls)

        # Get class name without the "Tool" suffix
        raw_name = cls.__name__
        if raw_name.endswith("Tool"):
            raw_name = raw_name[:-4]  # Remove "Tool"

        # Insert spaces before capital letters, excluding the first letter
        spaced = re.sub(r'(?<!^)(?=[A-Z])', ' ', raw_name)
        cls.name = spaced

    def update(self):
        """A call back given to the ToolsManager that updates the ToolData objects and their associated Components."""
        self._update_data()
        self._update_components()

    def _update_components(self):
        """Calls the update method on each component.

           Iterates through the components and displays the current values of their ToolData objects."""
        for component in self.view.components:
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