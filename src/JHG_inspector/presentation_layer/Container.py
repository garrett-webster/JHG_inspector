from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QContextMenuEvent
from PyQt6.QtWidgets import QSplitter, QWidget, QMenu, QLabel

from src.JHG_inspector.presentation_layer.components.TabbedPanels import TabbedPanels


class Container(QSplitter):
    """Used to create a runtime customizable layout.

       Each Container can hold up to two items (which can be either TabbedPanel objects, other Containers, or one
       of each). They are either displayed vertically or horizontally, based on the orientation passed at construction.
       By calling the split command, you can add either the second item, or if two already exist, replace an item with
       a new container with its first item being the replaced item. If both items are removed, the Container is deleted.
       """

    num_containers = 0

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal):
        """
        Parameters
        ----------
        orientation: Qt.Orientation
            Defines whether the items will be displayed one on top of the other (Qt.Orientation.Vertical), or side
            by side (Qt.Orientation.Horizontal).
        """

        Container.num_containers += 1
        self.container_num = Container.num_containers
        super().__init__()
        self.setOrientation(orientation)
        self.setHandleWidth(1)

    def add_child(self, widget: QWidget, split_direction: Qt.Orientation = Qt.Orientation.Horizontal, index: int = 1):
        """Adds a widget to a Container, nesting a new container if necessary.

           Adds a widget if there is only one item in the Container. Otherwise, creates a new Container, places the item
           at the index to be split in the new Container, adds the passed widget to the new Container, a replaces the
           item at the index to be split with the new Container.

           Parameters
           ----------
           widget: QWidget
               The new widget to be added
           index: int
               The index of the parent Container where the new widget should be placed (usually through instantiating a
               new Container and placing the widget in it)
           split_direction
               The orientation (horizontal or vertical) that the container the widget will be placed in should display
               its items. If the parent Container has only one item, that is the affected container. If it already has
               two, then the split_direction is applied to the new Container.
           """

        if self.count() == 1:
            self.setOrientation(split_direction)
            self.addWidget(widget)
            self.setCollapsible(1, False)
            self.setStretchFactor(self.indexOf(widget), 1)

            if isinstance(widget, TabbedPanels):
                widget.parent_container = self
        else:
            old_widget = self.widget(index)  # The widget at the position where the split is to occur


            nested_container = Container(orientation=split_direction)
            if old_widget:
                old_widget.setParent(nested_container)
                nested_container.addWidget(old_widget)
                nested_container.addWidget(widget)
                nested_container.setCollapsible(1, False)
            else:
                nested_container.addWidget(widget)


            nested_container.setCollapsible(0, False)

            if isinstance(widget, TabbedPanels):
                widget.parent_container = nested_container

            self.insertWidget(index, nested_container)
            self.setStretchFactor(self.indexOf(widget), 1)

    def empty_check(self):
        """A call back called by children Containers and TabbedPanels when they are cleared.

           Allows for Container's items to let the Container know when it should check if it is empty. If it is, it then
           propagates the empty_check up to its parent, allowing for all ancestor Containers to close once they have
           no more items in their tree.
           """

        if self.count() == 0:
            Container.num_containers -= 1

            parent_container = self.find_parent_container()

            self.setParent(None)
            self.deleteLater()

            if parent_container is not None:
                parent_container.empty_check()

    def find_parent_container(self):
        parent = self.parent()
        while parent and not isinstance(parent, Container):
            parent = parent.parent()
        return parent

    def contextMenuEvent(self, event: QContextMenuEvent):
        widget_under_mouse = self.childAt(event.pos())
        while widget_under_mouse and widget_under_mouse.parent() != self:
            widget_under_mouse = widget_under_mouse.parent()
        index = self.indexOf(widget_under_mouse)

        menu = QMenu(self)
        split_right = menu.addAction("Split Right")
        split_right.triggered.connect(partial(self.split, split_direction = Qt.Orientation.Horizontal, splitter_index=index))

        split_down = menu.addAction("Split Down")
        split_down.triggered.connect(partial(self.split, split_direction = Qt.Orientation.Vertical, splitter_index=index))

        menu.exec(event.globalPos())

    def split(self, widget: QWidget = None, split_direction: Qt.Orientation = Qt.Orientation.Horizontal, splitter_index=2):
        if not widget:
            widget = QLabel("New Widget")
        tabs = TabbedPanels(self.empty_check, new_widget = widget)
        self.add_child(tabs, split_direction, splitter_index)
