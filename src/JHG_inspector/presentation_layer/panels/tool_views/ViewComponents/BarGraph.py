from PyQt6.QtGui import QColor, QFont
import pyqtgraph as pg
from pyqtgraph import PlotWidget, BarGraphItem, TextItem


class BarGraph(PlotWidget):
    def __init__(self, data: "GraphToolData"):
        super().__init__()
        self.data = data

        self.vb = self.getPlotItem().getViewBox()

        # Hide axis completely (we'll draw our own)
        self.getPlotItem().showAxis("bottom", False)

        # Fixed baseline at y=0
        self._baseline = pg.InfiniteLine(
            angle=0, movable=False,
            pen=pg.mkPen((150, 150, 150), width=1)
        )
        self.addItem(self._baseline)

    def update(self, entry: int = 0):
        # Clear old bars/labels, keep baseline
        self.clear()
        self.addItem(self._baseline)

        # Validate data
        if not isinstance(self.data.list, list) or not all(isinstance(item, list) for item in self.data.list):
            raise TypeError("Expected data.to_list() to return a list of lists")

        # Compute max Y for padding
        all_y = [bar["data"][entry] for bar in self.data.entries if bar["data"]]
        y_max = max(all_y) if all_y else 1
        label_margin = -20 # space below baseline for labels

        # Draw bars + labels
        for i, bar in enumerate(self.data.entries):
            y_value = bar["data"][entry]
            label_text = bar["entry_name"]
            color = QColor(bar["color"])

            # Draw bar
            self.addItem(BarGraphItem(x=[i], height=[y_value], width=0.5, brush=color))

            # Draw label in data coordinates
            label_item = pg.TextItem(text=label_text, color="black")
            label_item.setAnchor((0, 0.5))  # horizontally center, stick bottom
            label_item.setRotation(270)  # vertical
            label_item.setPos(i, 0)  # slightly below baseline
            label_item.setZValue(10)  # ensure it’s on top
            self.addItem(label_item)

        # Set zoom limits: can't zoom out beyond current view, but can zoom in
        self.vb.setLimits(
            xMin=-0.5,
            xMax=len(self.data.entries) - 0.5,
            yMin=label_margin,
            yMax=y_max * 1.1
        )

        # Default zoomed-out view
        self.vb.setXRange(-0.5, len(self.data.entries) - 0.5)
        self.vb.setYRange(label_margin, y_max * 1.1)