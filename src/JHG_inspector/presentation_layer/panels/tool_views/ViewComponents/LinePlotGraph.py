from pyqtgraph import PlotWidget, mkPen, TextItem


class LinePlotGraph(PlotWidget):
    def __init__(self, data: "GraphToolData"):
        super().__init__()
        self.data = data

    def update(self):
        self.clear()
        # Check that the data in the ToolData is properly a list of lists.
        if not isinstance(self.data.list, list) or not all(isinstance(item, list) for item in self.data.list):
            raise TypeError("Expected data.to_list() to return a list of lists")

        for line in self.data.lines:
            x_values = list(range(len(line["data"])))
            y_values = line["data"]

            self.plot(x=x_values, y=y_values, pen=mkPen(color=line["color"], width = 2))

            if y_values:  # Check non-empty
                label = TextItem(text=line["line_name"], color=line["color"])
                label.setPos(x_values[-1], y_values[-1])
                self.addItem(label)