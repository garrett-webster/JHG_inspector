from collections.abc import Iterable

class ToolData:
    def __init__(self, data=None):
        self.data = data

    @property
    def raw(self):
        return self.data

    @property
    def to_str(self):
        return str(self.data)

    @property
    def to_list(self):
        if self.data is None:
            return []
        if isinstance(self.data, list):
            return self.data
        if isinstance(self.data, str):
            return [self.data]
        if isinstance(self.data, dict):
            return list(self.data.items())  # return (key, value) tuples
        if isinstance(self.data, Iterable):
            return list(self.data)
        return [self.data]