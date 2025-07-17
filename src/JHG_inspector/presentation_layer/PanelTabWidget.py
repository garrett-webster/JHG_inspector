from typing import Union

from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QTabWidget, QMenu, QApplication

from src.JHG_inspector.presentation_layer.components.DraggableTabBar import DraggableTabBar

class PanelTabWidget(QTabWidget):
    num_panels = 0
    def __init__(self, parent_container: "Container" = None, panel: "Panel" = None):
        super().__init__()
        with open("src/JHG_inspector/presentation_layer/stylesheets/TabbedPanels.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.setTabBar(DraggableTabBar())
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
        from src.JHG_inspector.presentation_layer.panels.CentralContainerRework import DefaultPanel
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
        if self.count() > 1:
            panel = self.widget(tab_index)
            self.remove_panel(panel)

            new_tabs = PanelTabWidget(self.parent_container, panel)
            self.parent_container.add_item(new_tabs, split_direction, self)

            panel.setFocus()

    def add_panel(self, panel: "Panel"):
        self.addTab(panel, panel.name)

    def remove_panel(self, panel_or_index: Union["Panel", int]):
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
        source_bar = event.source()
        if not isinstance(source_bar, DraggableTabBar):
            return

        source_widget = source_bar.parentWidget()
        target_widget = self
        if not isinstance(source_widget, PanelTabWidget):
            return

        index = int(event.mimeData().data("application/tab-index").data().decode("utf-8"))
        panel = source_widget.widget(index)

        source_widget.remove_panel(panel)
        target_widget.add_panel(panel)

        event.acceptProposedAction()

    def sizeHint(self):
        return QSize(600, 400)