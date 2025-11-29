class Resource:
    def __init__(self, transport, data):
        self.transport = transport
        self._data = data

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._data}>"
