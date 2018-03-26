import io
from typing import Union

class PluginFile:
    """
    Reference to a file for a plugin.
    """
    def __init__(self, target: str, local_path: str):
        self.target = target
        self.local_path = local_path


        # TODO handle folders?

    def content(self):
        with open(self.local_path, "r", encoding='UTF-8') as f:
            return  f.read()


class TextPluginFile:
    def __init__(self, target: str, content: Union[str,io.StringIO]):
        if isinstance(content, str):
            self._content = content
        else:
            self._content = content.getValue()

    def content(self):
        return self._content
