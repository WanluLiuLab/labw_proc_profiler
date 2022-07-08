import threading
from typing import List, Any

from pid_monitor._dt_mvc.appender import BaseTableAppender


class CSVTableAppender(BaseTableAppender):
    _write_mutex: threading.Lock

    def __init__(self, filename: str, header: List[str]):
        super().__init__(filename, header)
        self._write_mutex = threading.Lock()

    def _get_real_filename_hook(self):
        self._real_filename = ".".join((self.filename, "csv"))

    def _create_file_hook(self):
        with open(self._real_filename, "w") as writer:
            writer.write(",".join(self.header) + "\n")

    def append(self, body: List[Any]):
        write_str = ",".join(map(repr, body)) + "\n"
        with self._write_mutex, open(self._real_filename, "a") as writer:
            writer.write(write_str)
            writer.flush()

    def close(self):
        pass
