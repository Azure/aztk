import io
from typing import Union
from aztk.core.models import Model, fields


class PluginFile(Model):
    """
    Reference to a file for a plugin.
    """

    target = fields.String()
    local_path = fields.String()

    def __init__(self, target: str = None, local_path: str = None):
        super().__init__(target=target, local_path=local_path)

    def content(self):
        with open(self.local_path, "r", encoding="UTF-8") as f:
            return f.read()


class TextPluginFile(Model):
    """
    Reference to a file for a plugin.

    Args:
    target (str): Where should the file be uploaded relative to the plugin working dir
    content (str|io.StringIO): Content of the file. Can either be a string or a StringIO
    """

    target = fields.String()

    def __init__(self, target: str, content: Union[str, io.StringIO]):
        super().__init__(target=target)
        if isinstance(content, str):
            self._content = content
        else:
            self._content = content.getValue()

    def content(self):
        return self._content
