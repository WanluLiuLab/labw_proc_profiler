from typing import List, Any

from pid_monitor._dt_mvc.appender import BaseTableAppender


class TSVTableAppender(BaseTableAppender):
    def _create_file_hook(self):
        with open(self.filename, "w") as writer:
            writer.write("\t".join(self.header) + "\n")

    def append(self, body: List[Any]):
        with open(self.filename, "a") as writer:
            writer.write("\t".join(map(repr, body)) + "\n")
            writer.flush()
