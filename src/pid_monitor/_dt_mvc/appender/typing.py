import multiprocessing
import os
from abc import abstractmethod, ABC
from typing import List, Any, Dict

import pandas as pd


class TableAppenderConfig:
    buffer_size: int
    """
    Buffering strategy. 1 for no buffering.
    """

    def __init__(self, buffer_size: int = 1):
        self.buffer_size = buffer_size


class BaseTableAppender:
    filename: str
    header: List[str]
    _real_filename: str
    _tac: TableAppenderConfig

    def __init__(self, filename: str, header: List[str], tac: TableAppenderConfig):
        self.filename = filename
        self.header = header
        self._get_real_filename_hook()
        self._tac = tac
        if os.path.exists(self._real_filename):
            os.remove(self._real_filename)
        self._create_file_hook()

    @abstractmethod
    def _get_n_lines_actually_written_hook(self) -> int:
        pass

    def validate_lines(self, required_number_of_lines:int) -> None:
        actual_number_of_lines = self._get_n_lines_actually_written_hook()
        if actual_number_of_lines != required_number_of_lines:
            raise AssertionError(
                f"{self._real_filename}, "
                f"Required: {required_number_of_lines} "
                f"Actual: {actual_number_of_lines}"
            )

    @abstractmethod
    def _get_real_filename_hook(self):
        pass

    @abstractmethod
    def _create_file_hook(self):
        pass

    @abstractmethod
    def append(self, body: List[Any]):
        pass

    @abstractmethod
    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DictBuffer(BaseTableAppender, ABC):
    _h0: str
    _buff: Dict[str, List[Any]]
    _write_mutex: multiprocessing.Lock
    _buff_mutex: multiprocessing.Lock

    def __init__(self, filename: str, header: List[str], tac: TableAppenderConfig):
        super().__init__(filename, header, tac)
        self._buff_mutex = multiprocessing.Lock()
        self._write_mutex = multiprocessing.Lock()
        self._buff = {}
        self._h0 = self.header[0]

    def append(self, body: List[Any]):
        with self._buff_mutex:
            if self._buff == {}:
                self._buff = dict(zip(self.header, map(lambda x: [x], body)))
            else:
                for header_item, body_item in zip(self.header, body):
                    self._buff[header_item].append(body_item)
            if len(self) == self._tac.buffer_size:
                df = self.flush()
                self._buff = {}
                with self._write_mutex:
                    self._write_hook(df)

    @abstractmethod
    def _write_hook(self, df: Any):
        pass

    @abstractmethod
    def flush(self) -> Any:
        pass

    def __len__(self):
        if self._buff == {}:
            return 0
        return len(self._buff[self._h0])

    def close(self):
        if len(self) == 0:
            return
        df = self.flush()
        self._buff = {}
        with self._write_mutex:
            self._write_hook(df)


class PandasDictBuffer(DictBuffer, ABC):

    def flush(self) -> pd.DataFrame:
        df = pd.DataFrame.from_dict(data=self._buff)
        return df

    @abstractmethod
    def _write_hook(self, df: pd.DataFrame):
        pass
