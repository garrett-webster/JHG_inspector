from pyqtgraph import PlotWidget


class LinePlotGraph(PlotWidget):
    def __init__(self, data: "ToolData"):
        super().__init__()
        self.data = data

    def update(self):
        # Check that the data in the ToolData is properly a list of lists.
        if not isinstance(self.data.list, list) or not all(isinstance(item, list) for item in self.data.list):
            raise TypeError("Expected data.to_list() to return a list of lists")

        for line_data in self.data.list:
            x_values = list(range(len(line_data)))
            self.plot(x=x_values, y=line_data)