from typing import Callable

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QSplitter, QTabWidget, QLabel, QWidget

from src.JHG_inspector.presentation_layer.components.ContainerTabBar import ContainerTabBar

class Container(QSplitter):
    """Displays TabbedPanels objects and allows for custom runtime panel layouts.

    Each container is created with a TabbedPanels object by default. It can also have sub-containers added,
    which creates the custom panel layouts. If all tabs are closed, the TabbedPanels object is deleted. Similarly, if
    there are no tabs nor sub-containers, the Container object is deleted.
    """

    num_containers = 0
    def __init__(self, default_panel_check: Callable, parent=None):
        """
        Parameters
        ----------
        default_panel_check : Callable
            A function passed from the CentralPanel that checks if there are any panels left.
            If there are not, it displays a default pane. Each time a Container object is deleted,
            it calls default_panel_check.
        parent : QWidget, optional
            The QWidget that should be made the parent of the Container.
        """

        super().__init__(parent)
        Container.num_containers += 1
        self.num_containers += 1
        self.default_panel_check = default_panel_check

        self.orientation = Qt.Orientation.Horizontal
        self.tabs = self.TabbedPanels(self.check_is_empty)
        self.addWidget(self.tabs)

    # The orientation determines whether a child container will be displayed horizontally or vertically
    def set_orientation(self, orientation: Qt.Orientation):
        """
        Parameters
        ----------
        orientation : Qt.Orientation
            Used to define whether children Containers will be laid out horizontally or vertically.
        """
        self.orientation = orientation

    # To be empty, a container must have all tabs closed and not have a child container. If that is true, it deletes itself
    def check_is_empty(self):
        if self.tabs.count() == 0 and self.count() == 0:
            self.setParent(None)
            self.deleteLater()
            Container.num_containers -= 1
            self.default_panel_check()

    class DefaultTab(QLabel):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setText("New Tab")

    class TabbedPanels(QTabWidget):
        """A tabbed container for panel widgets.

        Allows for panels to occupy the same space. Panels can be dragged from any TabbedPanels object to another.
        Once the last tab is closed, the TabbedPanels object deletes itself.
        """

        def __init__(self, check_container_empty: Callable, parent: "Container"=None, widget: QWidget=None):
            """
            Parameters
            ----------
            check_container_empty : Callable
                A function passed from the parent Container that checks whether the Container is empty. TabbedPanels
                calls this function when the last tab is closed or moved to a different TabbedPanels.
            parent : QWidget, optional
                The QWidget that should be made the parent of the TabbedPanels.
            widget : QWidget, optional
                 The widget (usually a panel associated with a tool) that will be displayed as the first tab when the
                 TabbedPanels object is added.
            """
            super().__init__(parent)
            self.deleted = False
            self.check_container_empty = check_container_empty
            self.setTabBar(ContainerTabBar())
            self.setAcceptDrops(True)

            if widget is None:
                widget = Container.DefaultTab()
            self.addTab(widget, "New Tab")

            self.setTabsClosable(True)
            self.tabCloseRequested.connect(self.close_tab)

        def dragEnterEvent(self, event):
            if event.mimeData().hasFormat("application/x-tab-index"):
                event.acceptProposedAction()

        def dropEvent(self, event):
            if not event.mimeData().hasFormat("application/x-tab-index"):
                return

            source_tabbar = event.source()
            index_bytes = event.mimeData().data("application/x-tab-index")
            index = int(bytes(index_bytes).decode("utf-8"))

            source_tabwidget = source_tabbar.parentWidget()
            if not isinstance(source_tabwidget, Container.TabbedPanels):
                return

            panel = source_tabwidget.widget(index)
            label = source_tabwidget.tabText(index)

            source_tabwidget.removeTab(index)
            if source_tabwidget.count() == 0:
                source_tabwidget.deleted = True
                source_tabwidget.setParent(None)
                source_tabwidget.deleteLater()
                source_tabwidget.check_container_empty()

            # Tells the source container to check if it is empty after removing the tab
            source_container = source_tabwidget.parentWidget()
            if source_container and hasattr(source_container, 'check_is_empty'):
                source_container.check_is_empty()

            # Add to this widget
            self.addTab(panel, label)
            self.setCurrentWidget(panel)

            event.acceptProposedAction()

        # Closes the current tab. If that was the last tab, removes the TabbedPanels element
        def close_tab(self, index: int):
            widget = self.widget(index)
            self.removeTab(index)
            if widget is not None:
                widget.deleteLater()

            if self.count() == 0:
                self.deleted = True
                self.setParent(None)
                self.deleteLater()
                self.check_container_empty()

        def sizeHint(self):
            return QSize(600, 400)