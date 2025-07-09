from PyQt6.QtWidgets import QWidget

from src.JHG_inspector.logic_layer.tools.ToolDataClasses.ToolData import ToolData


class Component(QWidget):
    """An individual visual component that displays one set of data.

       Each component subclass represents one type of visual component. This could be something like a label-data pair,
       a graph, or any other kind of representation."""
    def __init__(self, parent, data: ToolData):
        super().__init__(parent)
        self.data = data

    def update(self):
        """Updates the elements in the component with the data stored in the attached ToolData object."""
        raise NotImplementedError("Subclasses must implement the update() method.")
