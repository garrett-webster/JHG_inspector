from typing import Union

from PyQt6.QtWidgets import QLabel, QVBoxLayout

from src.JHG_inspector.presentation_layer.Container import Container
from src.JHG_inspector.presentation_layer.PanelTabWidget import PanelTabWidget
from src.JHG_inspector.presentation_layer.panels.Panel import Panel


class CentralContainer(Container):
    def __init__(self):
        tab_widget = PanelTabWidget()
        super().__init__(tab_widget)
        tab_widget.parent_container = self
        default_panel = Panel()
        Panel.focused_panel = default_panel
        tab_widget.add_panel(default_panel)

    def remove_item(self, item: Union["Container", "Panel"]):
        super().remove_item(item)

        # After base logic runs, check if self is now empty
        if self.items[0] is None and self.items[1] is None:
            new_tab_widget = PanelTabWidget(self, DefaultPanel())
            self.items[0] = new_tab_widget
            self.addWidget(new_tab_widget)
            self.setCollapsible(0, False)

class DefaultPanel(Panel):
    num_panels = 0
    def __init__(self):
        super().__init__()
        DefaultPanel.num_panels += 1
        label = QLabel(str(DefaultPanel.num_panels))

        layout = QVBoxLayout()
        layout.addWidget(label)

        self.setLayout(layout)