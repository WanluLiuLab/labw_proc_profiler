from abc import abstractmethod
from typing import List, Any


class BaseTableAppender:
    filename: str
    header: List[str]
    _real_filename: str

    def __init__(self, filename: str, header: List[str]):
        self.filename = filename
        self.header = header
        self._get_real_filename_hook()
        self._create_file_hook()

    @abstractmethod
    def _get_real_filename_hook(self):
        pass

    @abstractmethod
    def _create_file_hook(self):
        pass

    @abstractmethod
    def append(self, body: List[Any]):
        pass
