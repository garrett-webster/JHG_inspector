from typing import Union, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSplitter

from src.JHG_inspector.presentation_layer.PanelTabWidget import PanelTabWidget


class Container(QSplitter):
    """Used to create custom layouts on the fly.

       Each Container can hold a maximum of two items (which is either another Container object or a PanelTabWidget).
       If another item is added, a new container is made and put in that place.
       """
    num_containers = 1
    def __init__(self, item: Union["Container", "PanelTabWidget"], parent_container: "Container" = None,
                 split_direction: Qt.Orientation = Qt.Orientation.Horizontal):
        super().__init__(parent_container)
        self.container_num = Container.num_containers
        Container.num_containers += 1

        self.parent_container = parent_container
        self.items = [item, None]
        self.setOrientation(split_direction)

        self.addWidget(item)
        self.setCollapsible(0, False)

    def add_item(self, new_item: Union["Container", "PanelTabWidget"],
                 split_direction: Qt.Orientation = Qt.Orientation.Horizontal, existing_item: Optional[Union["Container", "PanelTabWidget"]] = None):
        """Adds a new item to the container.

           If there are already two items in the Container, a new Container is created, the panel that was already there
           is added to the new Container, and that panel is replaced with the new Container.
           """

        if not self.items[1]:
            self.items[1] = new_item
            self.addWidget(new_item)
            self.setOrientation(split_direction)
            self.setCollapsible(1, False)
        elif existing_item:
            new_container = Container(existing_item, self, split_direction)
            self.replace_item(existing_item, new_container)
            new_container.add_item(new_item, split_direction)
            existing_item.parent_container = new_container
            new_item.parent_container = new_container

        else:
            raise ValueError("Panel must be provided when both items are occupied — the Container needs to know which "
                             "side to split.")

    def remove_item(self, item: Union["Container", "PanelTabWidget"]):
        """Removes the item from the container, and removes itself if it is now empty."""
        if item not in self.items:
            raise ValueError("Item not in this Container.")

        item.setParent(None)
        item.deleteLater()

        if item == self.items[0]:
            # If the Container has two elements, promote the 2nd item to the first item. If not, the Container will be
            # empty following the deletion of the 1st item, and should be removed from the parent Container
            if self.items[1]:
                promoted = self.items[1]
                self.items[0] = promoted
                self.items[1] = None
            elif self.parent_container: # Makes it so that a CentralContainer doesn't call parent_container.remove_item
                self.parent_container.remove_item(self)
            else:
                self.items[0] = None
        else:
            self.items[1] = None

    def replace_item(self, old_item: Union["Container", "Panel"], new_item: Union["Container", "Panel"]):
        """Replaces an item with a new one. Used for both collapsing structures of Containers that only hold other
           Containers and for putting new containers in the place of panels that will be split."""
        index = self.items.index(old_item)
        if index == -1:
            raise ValueError("Item not found in this Container.")

        old_item.setParent(new_item)
        new_item.addWidget(old_item)

        self.addWidget(new_item)
        self.items[index] = new_item

    def focus_first_panel(self):
        if isinstance(self.items[0], PanelTabWidget):
            self.items[0].widget(0).setFocus()
            return True
        elif isinstance(self.items[1], PanelTabWidget):
            self.items[1].widget(0).setFocus()
            return True
        elif self.items[0].focus_first_panel():
            return True
        elif self.items[1].focus_first_panel():
            return True
        else:
            return False

    def on_close(self):
        structure = [self.orientation().name, None, None]

        structure[1] = self.items[0].on_close()

        if self.items[1]:
            structure[2] = self.items[1].on_close()

        return structure