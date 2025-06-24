from functools import partial
from typing import override

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QPushButton

from src.JHG_inspector.presentation_layer.Container import Container
from src.JHG_inspector.presentation_layer.components.TabbedPanels import TabbedPanels


class CentralContainer(Container):
    def __init__(self, parent=None):
        """The root container for container structures.

        If all TabbedPanels and other Containers are closed, a new DefaultTab will be added."""

        super().__init__()
        widget = TabbedPanels(self.empty_check)
        self.addWidget(widget)
        widget.setParent(self)
        widget.parent_container = self
        self.setParent(parent)
        self.has_direct_child = True

    @override
    def empty_check(self):
        """A call back called by children Containers and TabbedPanels when they are cleared.

           Allows for Container's items to let the CentralContainer know when it should check if it is empty.
           """

        if self.count() == 0:
            self.has_direct_child = False
        if Container.num_containers == 1 and not self.has_direct_child:
            widget = DefaultTab(self)
            tabs = TabbedPanels(self.empty_check, self, widget)
            self.addWidget(tabs)
            self.has_direct_child = True


class DefaultTab(QWidget):
    """Displays when no other tabs are open in the GUI."""
    def __init__(self, parent: CentralContainer = None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel("No tools open.")
        open_button = QPushButton("Open New Tool")
        ''' TODO: Once the ToolManager has been created, use a dialog to select the tool and pass that as the widget 
            Will also want to find a way to replace the DefaultTab with that widget instead of calling split and
            opening a new panel'''
        open_button.clicked.connect(partial(parent.split, Qt.Orientation.Horizontal, 0))
        layout.addStretch()
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(open_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)
