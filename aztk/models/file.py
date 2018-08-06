import io


class File:
    def __init__(self, name: str, payload: io.StringIO):
        self.name = name
        self.payload = payload
