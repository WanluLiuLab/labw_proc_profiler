from typing import List, Any

from pid_monitor._dt_mvc.appender import BaseTableAppender


class TSVTableAppender(BaseTableAppender):
    def __init__(self, filename: str, header: List[str]):
        super().__init__(filename, header)

    def _get_real_filename_hook(self):
        self._real_filename = ".".join((self.filename, "tsv"))

    def _create_file_hook(self):
        with open(self._real_filename, "w") as writer:
            writer.write("\t".join(self.header) + "\n")

    def append(self, body: List[Any]):
        with open(self._real_filename, "a") as writer:
            writer.write("\t".join(map(repr, body)) + "\n")
            writer.flush()
