from src.JHG_inspector.logic_layer.tools.ToolDataClasses.ToolData import ToolData


class DataLabelToolData(ToolData):
    def __init__(self, name: str, data = None):
        super().__init__(data)
        self.name = name
