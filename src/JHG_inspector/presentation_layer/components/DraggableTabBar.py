from PyQt6.QtWidgets import QTabBar
from PyQt6.QtCore import Qt, QMimeData, QPoint
from PyQt6.QtGui import QDrag


class DraggableTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setAcceptDrops(True)
        self.drag_start_pos = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.pos() - self.drag_start_pos).manhattanLength() < 10:
            return

        index = self.tabAt(self.drag_start_pos)
        if index < 0:
            return

        tab_text = self.tabText(index)
        mime_data = QMimeData()
        mime_data.setText(tab_text)
        mime_data.setData("application/tab-index", bytes(str(index), encoding="utf-8"))

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/tab-index"):
            event.acceptProposedAction()

    def dropEvent(self, event):
        from src.JHG_inspector.presentation_layer.PanelTabWidget import PanelTabWidget
        source_bar = event.source()
        if not isinstance(source_bar, DraggableTabBar):
            return

        source_widget = source_bar.parentWidget()
        target_widget = self.parentWidget()
        if not isinstance(source_widget, PanelTabWidget) or not isinstance(target_widget, PanelTabWidget):
            return

        index = int(event.mimeData().data("application/tab-index").data().decode("utf-8"))
        panel = source_widget.widget(index)

        # Remove from source
        source_widget.remove_panel(panel)

        # Add to target
        target_widget.add_panel(panel)

        event.acceptProposedAction()