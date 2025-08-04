from typing import Union

from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QTabWidget, QMenu, QApplication

from src.JHG_inspector.presentation_layer.components.ContainerTabBar import ContainerTabBar

class PanelTabWidget(QTabWidget):
    """A collection of tabbed panels, where only one panel is visible at a time.

       A PanelTabWidget serves as the intermediary between the purely structural Container Objects and the Panel objects
       which contain the actual content to be displayed. Panels can be dragged from one PanelTabWidget to another. If a
       PanelTabWidget is emptied (either by closing the last tab or by dragging it to a different PanelTabWidget), it
       tells its parent container that it should be removed.
       """

    num_panels = 0
    def __init__(self, parent_container: "Container" = None, panel: "Panel" = None):
        super().__init__()
        with open("src/JHG_inspector/presentation_layer/stylesheets/TabbedPanels.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.setTabBar(ContainerTabBar())
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setAcceptDrops(True)  # Enable drop events

        self.parent_container = parent_container

        PanelTabWidget.num_panels += 1
        self.panel_num = PanelTabWidget.num_panels

        self.tabCloseRequested.connect(self.remove_panel)

        if panel is not None:
            self.add_panel(panel)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

    def open_context_menu(self, pos: QPoint):
        from src.JHG_inspector.presentation_layer.panels.CentralContainer import DefaultPanel
        tab_index = self.tabBar().tabAt(pos)
        if tab_index == -1:
            return  # Clicked outside any tab

        menu = QMenu(self)

        close_action = QAction("Close Tab", self)
        close_action.triggered.connect(lambda: self.remove_panel(tab_index))


        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(lambda: self.add_panel(DefaultPanel()))

        if self.count() > 1:
            split_right_action = QAction("Split Right", self)
            split_right_action.triggered.connect(lambda: self.split(tab_index, Qt.Orientation.Horizontal))
            split_down_action = QAction("Split Down", self)
            split_down_action.triggered.connect(lambda: self.split(tab_index, Qt.Orientation.Vertical))
        else:
            split_right_action = QAction("Split Right", self)
            split_right_action.setEnabled(False)
            split_down_action = QAction("Split Down", self)
            split_down_action.setEnabled(False)

        menu.addAction(close_action)
        menu.addAction(split_right_action)
        menu.addAction(split_down_action)
        menu.addAction(new_tab_action)
        menu.exec(self.mapToGlobal(pos))

    def split(self, tab_index: int, split_direction: Qt.Orientation):
        """Creates a new PanelTabWidget with the selected panel and adds it either to the right or below this
           PanelTabWidget."""
        if self.count() > 1:
            panel = self.widget(tab_index)
            self.remove_panel(panel)

            new_tabs = PanelTabWidget(self.parent_container, panel)
            self.parent_container.add_item(new_tabs, split_direction, self)

            panel.setFocus()

    def add_panel(self, panel: "Panel"):
        """Creates a new tab out of the passed Panel object"""
        self.addTab(panel, panel.name)

    def remove_panel(self, panel_or_index: Union["Panel", int]):
        """Removes the specified panel (passed as a panel or as a tab index). If by removing the panel the
           PanelTabWidget is now empty, tells its parent container that it should be removed."""
        if isinstance(panel_or_index, int):
            panel = self.widget(panel_or_index)
        else:
            panel = panel_or_index

        index = self.indexOf(panel)
        if index != -1:
            self.removeTab(index)

        if self.count() == 0 and self.parent_container:
            self.parent_container.remove_item(self)
            main_window = QApplication.instance().main_window
            main_window.body_splitter.central_panel.focus_first_panel()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/tab-index"):
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Allows for panels to be dropped into the PanelTabWidget."""
        source_bar = event.source()
        if not isinstance(source_bar, ContainerTabBar):
            return

        source_widget = source_bar.parentWidget()
        target_widget = self
        if not isinstance(source_widget, PanelTabWidget):
            return

        if source_widget == self:
            return

        index = int(event.mimeData().data("application/tab-index").data().decode("utf-8"))
        panel = source_widget.widget(index)

        source_widget.remove_panel(panel)
        target_widget.add_panel(panel)

        new_index = target_widget.indexOf(panel)
        target_widget.setCurrentIndex(new_index)

        event.acceptProposedAction()

    def on_close(self):
        from src.JHG_inspector.presentation_layer.panels.tool_views.View import View
        tools = []
        for i in range(self.count()):
            if isinstance(self.widget(i), View):
                tools.append(self.widget(i).tool.name)
            else:
                tools.append(None)

        return tuple(item for item in tools)

    def sizeHint(self):
        return QSize(600, 400)