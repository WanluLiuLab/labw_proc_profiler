from typing import List, Any

from pid_monitor._dt_mvc.appender import BaseTableAppender
from pid_monitor._dt_mvc.appender.typing import TableAppenderConfig


class DumbTableAppender(BaseTableAppender):

    def _get_n_lines_actually_written_hook(self) -> int:
        return 0

    def validate_lines(self, required_number_of_lines:int) -> None:
        pass

    def __init__(self, filename: str, header: List[str], tac:TableAppenderConfig):
        super().__init__(filename, header, tac)

    def _get_real_filename_hook(self):
        self._real_filename = ""

    def _create_file_hook(self):
        pass

    def append(self, body: List[Any]):
        pass

    def close(self):
        pass
