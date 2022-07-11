import os

import pandas as pd

from pid_monitor._dt_mvc.appender.typing import PandasDictBufferAppender


class HDF5TableAppender(PandasDictBufferAppender):
    def _get_n_lines_actually_written_hook(self) -> int:
        return pd.read_hdf(self._real_filename, key="df").shape[0]

    def _get_real_filename_hook(self):
        self._real_filename = ".".join((self.filename, "hdf5"))

    def _create_file_hook(self):
        pass

    def _write_hook(self, df: pd.DataFrame):
        df.to_hdf(self._real_filename, key="df", format='table', append=os.path.exists(self._real_filename))
