from collections.abc import Iterable

class ToolData:
    def __init__(self, data=None):
        self.raw = data

    @property
    def str(self):
        return str(self.raw)

    @property
    def list(self):
        if self.raw is None:
            return []
        if isinstance(self.raw, list):
            return self.raw
        if isinstance(self.raw, str):
            return [self.raw]
        if isinstance(self.raw, dict):
            return list(self.raw.items())  # return (key, value) tuples
        if isinstance(self.raw, Iterable):
            return list(self.raw)
        return [self.raw]