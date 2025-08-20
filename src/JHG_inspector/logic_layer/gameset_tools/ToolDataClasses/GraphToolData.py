from src.JHG_inspector.logic_layer.gameset_tools.ToolDataClasses.ToolData import ToolData

DEFAULT_COLORS = [
    "#FF9191",
    "#D15C5E",
    "#965875",
    "#FFF49F",
    "#B1907D",
    "#FFAFD8",
    "#C9ADE9",
    "#FDBF6F",
    "#A6CEE3",
    "#BFD3A6",
    "#888888",
    "#FA7900",
    "#FF3235",
    "#CE73CF",
    "#9C4ECF",
    "#7072F7",
    "#1F78B4",
    "#5F9CC7",
    "#12A79D",
    "#1AE3BE",
    "#B9F7EC",
    "#A4E436",
    "#1F9717",
    "#FFFFFF",
    "#997500",
    "#8D4118",
]

class GraphToolData(ToolData):
    def __init__(self, data=None):
        super().__init__(data)

        self.entries: list[dict[str, list[int] | str]] = []
        self.num_colors_used = 0

    def add_entry(self, entry_name: str, data: list[int], color: str = None) -> None:
        if not color:
            color = DEFAULT_COLORS[self.num_colors_used % len(DEFAULT_COLORS)]
            self.num_colors_used += 1
        self.entries.append({"entry_name": entry_name, "data": data, "color": color})

    def clear_entries(self):
        self.entries = []
        self.num_colors_used = 0
