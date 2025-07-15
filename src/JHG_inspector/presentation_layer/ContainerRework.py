from typing import Union, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSplitter

from src.JHG_inspector.presentation_layer.PanelTabWidget import PanelTabWidget
from src.JHG_inspector.presentation_layer.panels.Panel import Panel


class Container(QSplitter):
    """Used to create custom layouts on the fly.

       Each Container can hold a maximum of two items (which is either another Container object or a PanelTabWidget).
       If another item is added, a new container is made and put in that place.
       """

    def __init__(self, item: Union["Container", "PanelTabWidget"], parent_container: "Container" = None,
                 split_direction: Qt.Orientation = Qt.Orientation.Horizontal):
        super().__init__(parent_container)

        self.parent_container = parent_container
        self.items = [item, None]
        self.setOrientation(split_direction)

        self.addWidget(item)
        self.setCollapsible(0, False)

    def add_item(self, new_item: Union["Container", "PanelTabWidget"],
                 split_direction: Qt.Orientation = Qt.Orientation.Horizontal, panel: Optional[Panel] = None):
        """Adds a new item to the container.

           If there are already two items in the Container, a new Container is created, the panel that was already there
           is added to the new Container, and that panel is replaced with the new Container.
           """

        if not self.items[1]:
            self.items[1] = new_item
            self.addWidget(new_item)
            self.setOrientation(split_direction)
            self.setCollapsible(1, False)
        elif panel:
            new_container = Container(panel, self, split_direction)
            new_container.add_item(new_item)

            self.replace_item(panel, new_container)

        else:
            raise ValueError("Panel must be provided when both items are occupied — the Container needs to know which "
                             "side to split.")

    def remove_item(self, item: Union["Container", "Panel"]):
        """Removes the item from the container, and removes itself if it is now empty."""
        if item not in self.items:
            raise ValueError("Item not in this Container.")

        self.removeWidget(item)
        item.setParent(None)
        item.deleteLater()

        if item == self.items[0]:
            if self.items[1]:
                promoted = self.items[1]
                self.removeWidget(promoted)
                self.items[0] = promoted
                self.items[1] = None
                self.addWidget(promoted)
                self.setCollapsible(0, False)
            else:
                self.parent_container.remove_item(self)
                return
        else:
            self.items[1] = None

    def replace_item(self, old_item: Union["Container", "Panel"], new_item: Union["Container", "Panel"]):
        """Replaces an item with a new one. Used for both collapsing structures of Containers that only hold other
           Containers and for putting new containers in the place of panels that will be split."""
        index = self.indexOf(old_item)
        if index == -1:
            raise ValueError("Item not found in this Container.")

        self.removeWidget(old_item)
        old_item.setParent(None)
        old_item.deleteLater()

        self.insertWidget(index, new_item)
        self.items[index] = new_item


