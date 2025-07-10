from typing import Callable

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QTabWidget, QWidget, QLabel

from src.JHG_inspector.presentation_layer.components.ContainerTabBar import ContainerTabBar


class TabbedPanels(QTabWidget):
    num_tabs = 0
    """A tabbed container for panel widgets.

    Allows for panels to occupy the same space. Panels can be dragged from any TabbedPanels object to another.
    Once the last tab is closed, the TabbedPanels object deletes itself.
    """

    def __init__(self, check_container_empty: Callable, parent: "Container" = None, new_widget: QWidget = None):
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
        with open("src/JHG_inspector/presentation_layer/stylesheets/TabbedPanels.qss", "r") as f:
            self.setStyleSheet(f.read())


        TabbedPanels.num_tabs += 1
        self.deleted = False
        self.check_container_empty = check_container_empty
        self.parent_container = parent

        self.setTabBar(ContainerTabBar())
        self.setAcceptDrops(True)

        self.new_widget = new_widget
        if self.new_widget is None:
            self.new_widget = QLabel(str(TabbedPanels.num_tabs))
        self.addTab(self.new_widget, str(TabbedPanels.num_tabs))

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
        if not isinstance(source_tabwidget, TabbedPanels):
            return

        if source_tabwidget is self:
            return

        panel = source_tabwidget.widget(index)
        label = source_tabwidget.tabText(index)

        source_tabwidget.removeTab(index)
        if source_tabwidget.count() == 0:
            source_tabwidget.setParent(None)
            source_tabwidget.deleteLater()
            if source_tabwidget.parent_container:
                source_tabwidget.parent_container.empty_check()

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
            self.setParent(None)
            self.deleteLater()
            if self.parent_container is not None:
                self.parent_container.empty_check()

    def sizeHint(self):
        return QSize(600, 400)