import os
import threading
from typing import List, Any

import fastparquet as fp
import pandas as pd

from pid_monitor._dt_mvc.appender import BaseTableAppender


class ParquetTableAppender(BaseTableAppender):
    _write_mutex: threading.Lock
    _header: List[str]

    def __init__(self, filename: str, header: List[str]):
        super().__init__(filename, header)
        self._write_mutex = threading.Lock()
        self._header = header

    def _get_real_filename_hook(self):
        self._real_filename = ".".join((self.filename, "parquet"))

    def _create_file_hook(self):
        pass

    def append(self, body: List[Any]):
        df = pd.DataFrame.from_dict(data=dict(zip(self._header, map(lambda x: [x], body))))
        with self._write_mutex:
            fp.write(self._real_filename, df, append=os.path.exists(self._real_filename))
            # if not os.path.exists(self._real_filename):
            #     df.to_parquet(self._real_filename, engine="fastparquet")
            # else:
            #     # df.to_parquet(self._real_filename, engine="fastparquet", append=True)
            #     fp.write(self._real_filename, df, append=True)

    def close(self):
        pass
