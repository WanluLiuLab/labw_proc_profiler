from typing import List, Any

from pid_monitor._dt_mvc.appender import BaseTableAppender


class DumbTableAppender(BaseTableAppender):

    def __init__(self, filename: str, header: List[str]):
        super().__init__(filename, header)

    def _get_real_filename_hook(self):
        self._real_filename = ""

    def _create_file_hook(self):
        pass

    def append(self, body: List[Any]):
        pass

    def close(self):
        pass
