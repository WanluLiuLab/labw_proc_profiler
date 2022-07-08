import os
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
        if os.path.exists(self._real_filename):
            os.remove(self._real_filename)
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

    @abstractmethod
    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
