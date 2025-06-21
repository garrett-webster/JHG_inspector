from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QSplitter, QTabWidget, QLabel

from src.JHG_inspector.presentation_layer.components.ContainerTabBar import ContainerTabBar


class Container(QSplitter):
    num_containers = 0
    def __init__(self, default_panel_check, parent=None):
        super().__init__(parent)
        Container.num_containers += 1
        self.num_containers += 1
        self.default_panel_check = default_panel_check

        self.orientation = Qt.Orientation.Horizontal
        self.tabs = self.TabbedPanels(self.check_is_empty)
        self.addWidget(self.tabs)

    def set_orientation(self, orientation: Qt.Orientation):
        self.orientation = orientation

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
        def __init__(self, check_container_empty, parent=None, widget=None):
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

            source_container = source_tabwidget.parentWidget()
            if source_container and hasattr(source_container, 'check_is_empty'):
                source_container.check_is_empty()

            # Add to this widget
            self.addTab(panel, label)
            self.setCurrentWidget(panel)

            event.acceptProposedAction()

        def close_tab(self, index):
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