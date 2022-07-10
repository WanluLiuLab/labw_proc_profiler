"""
Using arrow IPC format with one record per block.

This application have bugs.
"""

from typing import List, Optional

import pandas as pd
import pyarrow as pa

from pid_monitor._dt_mvc.appender.typing import TableAppenderConfig, DictBuffer


class ArrowTableAppender(DictBuffer):
    _schema: Optional[pa.Schema]
    _file_handler: Optional[pa.RecordBatchStreamWriter]

    def _get_n_lines_actually_written_hook(self) -> int:
        return pa.ipc.open_stream(pa.OSFile(self._real_filename)).read_all().to_pandas().shape[0]

    def __init__(self, filename: str, header: List[str], tac: TableAppenderConfig):
        super().__init__(filename, header, tac)
        self._schema = None
        self._file_handler = None

    def _get_real_filename_hook(self):
        self._real_filename = ".".join((self.filename, "arrow"))

    def _create_file_hook(self):
        pass

    def _write_hook(self, df: pa.RecordBatch):
        if self._schema is None:
            self._schema = df.schema
            self._file_handler = pa.ipc.new_stream(
                sink=pa.OSFile(self._real_filename, mode="w"),
                schema=df.schema
            )
        self._file_handler.write_batch(df)

    def flush(self) -> pa.RecordBatch:
        return pa.record_batch(pd.DataFrame.from_dict(data=self._buff))

    def close(self):
        super(ArrowTableAppender, self).close()
        if self._file_handler is None:
            return
        self._file_handler.close()
