from typing import Dict, ClassVar, Optional

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget, QMenu

from src.JHG_inspector.presentation_layer.PanelTabWidget import PanelTabWidget


class Panel(QWidget):
    focused_panel: ClassVar[Optional["Panel"]] = None
    def __init__(self, parent=None, name: str = "Untitled"):
        super().__init__(parent)
        self.name = name

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

    def open_context_menu(self, pos: QPoint, actions: Dict[str, QAction] = None):
        menu = QMenu(self)

        close_action = QAction("Close This Tab", self)
        close_action.triggered.connect(self.close_self)

        if self.get_parent_tabwidget().count() > 1:
            split_right = QAction("Split Right", self)
            split_right.triggered.connect(lambda: self.split_self(Qt.Orientation.Horizontal))

            split_down = QAction("Split Down", self)
            split_down.triggered.connect(lambda: self.split_self(Qt.Orientation.Vertical))
        else:
            split_right = QAction("Split Right", self)
            split_right.setEnabled(False)

            split_down = QAction("Split Down", self)
            split_down.setEnabled(False)

        menu.addAction(close_action)
        menu.addAction(split_right)
        menu.addAction(split_down)

        if actions:
            for title, action in actions.items:
                menu.addAction(action.key(), action.value())

        menu.exec(self.mapToGlobal(pos))

    def close_self(self):
        tab_widget = self.get_parent_tabwidget()
        if tab_widget:
            tab_widget.remove_panel(self)

    def split_self(self, orientation: Qt.Orientation):
        tab_widget = self.get_parent_tabwidget()
        if tab_widget and tab_widget.parent_container:
            tab_index = tab_widget.indexOf(self)
            tab_widget.split(tab_index, orientation)

    def get_parent_tabwidget(self) -> "PanelTabWidget":
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, PanelTabWidget):
                return parent
            parent = parent.parent()
        return None

    def focusInEvent(self, event):
        Panel.focused_panel = self
        super().focusInEvent(event)
        print(f"Focused on {self}")