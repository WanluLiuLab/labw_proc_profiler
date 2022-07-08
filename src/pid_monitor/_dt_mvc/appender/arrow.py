"""
Using arrow IPC format with one record per block.
"""

import threading
from typing import List, Any, Optional

import pyarrow as pa

from pid_monitor._dt_mvc.appender import BaseTableAppender


class ArrowTableAppender(BaseTableAppender):
    _write_mutex: threading.Lock
    _header: List[str]

    _schema: Optional[pa.Schema]
    _file_handler: Optional[pa.RecordBatchStreamWriter]

    def __init__(self, filename: str, header: List[str]):
        super().__init__(filename, header)
        self._write_mutex = threading.Lock()
        self._header = header
        self._schema = None
        self._file_handler = None

    def _get_real_filename_hook(self):
        self._real_filename = ".".join((self.filename, "arrow"))

    def _create_file_hook(self):
        pass

    def append(self, body: List[Any]):
        record_batch = pa.record_batch(data=list(map(lambda x: [x], body)), names=self._header)
        if self._schema is None:
            self._schema = record_batch.schema
            with self._write_mutex:
                self._file_handler = pa.ipc.new_stream(
                    sink=pa.OSFile(self._real_filename, mode="w"),
                    schema=record_batch.schema
                )
        else:
            with self._write_mutex:
                self._file_handler.write_batch(record_batch)

    def close(self):
        if self._file_handler is not None:
            self._file_handler.close()
