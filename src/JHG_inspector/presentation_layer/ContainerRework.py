from typing import Union, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSplitter

from src.JHG_inspector.presentation_layer.PanelTabWidget import PanelTabWidget
from src.JHG_inspector.presentation_layer.panels.Panel import Panel


class Container(QSplitter):
    def __init__(self, item: Union["Container", "PanelTabWidget"], parent_container: "Container" = None,
                 split_direction: Qt.Orientation = Qt.Orientation.Horizontal):
        super().__init__(parent_container)

        self.parent_container = parent_container
        self.items = [item, None]
        self.setOrientation(split_direction)

        self.addWidget(item)
        self.setCollapsible(0, False)

    def add_item(self, new_item: Union["Container", "PanelTabWidget"], split_direction: Qt.Orientation = Qt.Orientation.Horizontal, panel: Optional[Panel] = None):
        if not self.items[1]:
            self.items[1] = new_item
            self.addWidget(new_item)
            self.setOrientation(split_direction)
            self.setCollapsible(1, False)
        elif panel:
            index = self.indexOf(panel)
            if index == -1:
                raise ValueError("Panel not found in this Container.")

            old_item = self.items[index]
            new_container = Container(old_item, self, split_direction)
            new_container.add_item(new_item)
            self.insertWidget(index, new_container)
            self.items[index] = new_container

        else:
            raise ValueError("Panel must be provided when both items are occupied — the Container needs to know which "
                             "side to split.")

