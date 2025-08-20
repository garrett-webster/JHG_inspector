from pyqtgraph import PlotWidget, mkPen, TextItem


class LinePlotGraph(PlotWidget):
    def __init__(self, data: "GraphToolData"):
        super().__init__()
        self.data = data

        self.vb = self.getPlotItem().getViewBox()
        self.getPlotItem().enableAutoRange(x=True, y=True)

    def update(self):
        self.clear()
        # Check that the data in the ToolData is properly a list of lists.
        if not isinstance(self.data.list, list) or not all(isinstance(item, list) for item in self.data.list):
            raise TypeError("Expected data.to_list() to return a list of lists")

        for line in self.data.entries:
            x_values = list(range(len(line["data"])))
            y_values = line["data"]

            self.plot(x=x_values, y=y_values, pen=mkPen(color=line["color"], width = 2))

            if y_values:  # Check non-empty
                label = TextItem(text=line["entry_name"], color=line["color"])
                label.setPos(x_values[-1], y_values[-1])  # small offset
                self.addItem(label)

        """Add padding so that the player name labels aren't cut off."""
        all_x = []
        all_y = []
        for line in self.data.entries:
            all_x.extend(range(len(line["data"])))
            all_y.extend(line["data"])

        if all_x and all_y:
            x_min, x_max = min(all_x), max(all_x)
            y_min, y_max = min(all_y), max(all_y)

            # Add small padding
            x_pad = (x_max - x_min) * 0.1 or 1
            y_pad = (y_max - y_min) * 0.1 or 1

            self.vb.setXRange(x_min, x_max + x_pad)
            self.vb.setYRange(y_min, y_max + y_pad)