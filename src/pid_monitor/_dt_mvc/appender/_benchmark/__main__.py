import multiprocessing
import os
import random
import string
import time
from typing import Iterable

import tqdm

from pid_monitor._dt_mvc.appender import load_table_appender_class, BaseTableAppender, AVAILABLE_TABLE_APPENDERS
from pid_monitor._dt_mvc.appender.typing import TableAppenderConfig


def bench_multithread(
        _appender_class_name: str,
        _thread_num: int,
        _run_id: int,
        _final_result_appender: BaseTableAppender,
        tac: TableAppenderConfig
):
    class AppenderProcess(multiprocessing.Process):
        def __init__(
                self,
                _appender: BaseTableAppender,
                n_line: int
        ):
            super().__init__()
            self.appender = _appender
            self.n_line = n_line

        def run(self):
            for i in range(self.n_line):
                self.appender.append([
                    i,
                    random.random(),
                    random.choice(''.join(random.choices(string.ascii_letters, k=5))),
                    random.randint(1, 5),
                    time.time()
                ])
            self.appender.close()

    appender = load_table_appender_class(_appender_class_name)(
        "test",
        ["INDEX", "RAND_FLOAT", "RAND_STR", "RAND_INT", "TIME"],
        tac
    )
    ts = time.time()
    process_pool = []
    total_n_lines = 1000 // _thread_num * _thread_num
    for _ in range(_thread_num):
        process_pool.append(AppenderProcess(appender, n_line=total_n_lines // _thread_num))
        process_pool[-1].start()
    for i in range(_thread_num):
        process_pool[i].join()
    te = time.time()
    appender.close()
    appender.validate_lines(total_n_lines)
    if appender._real_filename != "":
        os.remove(appender._real_filename)
    _final_result_appender.append([
        _appender_class_name,
        _thread_num,
        tac.buffer_size,
        _run_id,
        te - ts
    ])


def bench(thread_nums: Iterable[int], buffer_sizes: Iterable[int]):
    try:
        os.remove("bench_result.tsv")
    except FileNotFoundError:
        pass
    final_result_appender = load_table_appender_class("TSVTableAppender")(
        "bench_result",
        ["APPENDER_CLASS_NAME", "THREAD_NUM", "BUFF_SIZE", "RUN_ID", "TIME_SPENT"],
        TableAppenderConfig(1)
    )
    for appender_class_name in AVAILABLE_TABLE_APPENDERS:
        for thread_num in thread_nums:
            for buffer_size in buffer_sizes:
                desc = f"{appender_class_name}: threads={thread_num}, buffer={buffer_size}"
                for run_id in tqdm.tqdm(range(40), desc=desc):
                    bench_multithread(
                        appender_class_name,
                        thread_num,
                        run_id,
                        final_result_appender,
                        TableAppenderConfig(buffer_size)
                    )
        print(f"Benchmarking {appender_class_name} FIN")
    final_result_appender.close()


if __name__ == '__main__':
    bench(
        [1, 3],
        [1, 3]
    )
    bench(
        range(1, 2 * multiprocessing.cpu_count() + 1, 10),
        [1, 4, 16, 64, 256, 1024]
    )
