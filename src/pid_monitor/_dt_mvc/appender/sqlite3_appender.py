import sqlite3

import pandas as pd

from pid_monitor._dt_mvc.appender.typing import PandasDictBufferAppender


class SQLite3TableAppender(PandasDictBufferAppender):

    def _get_n_lines_actually_written_hook(self) -> int:
        with sqlite3.connect(self._real_filename) as con:
            return pd.read_sql_query("SELECT * FROM db", con=con).shape[0]

    def _get_real_filename_hook(self):
        self._real_filename = ".".join((self.filename, "sqlite3"))

    def _create_file_hook(self):
        pass

    def _write_hook(self, df: pd.DataFrame):
        with sqlite3.connect(self._real_filename) as con:
            df.to_sql(name="db", con=con, if_exists="append")
