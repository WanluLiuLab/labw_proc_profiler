import multiprocessing
import os
import random
import string
import time

import tqdm

from pid_monitor._dt_mvc.appender import load_table_appender_class, BaseTableAppender, AVAILABLE_TABLE_APPENDERS


def bench_multithread(
        _appender_class_name: str,
        _thread_num: int,
        _run_id: int,
        _final_result_appender: BaseTableAppender
):
    class AppenderProcess(multiprocessing.Process):
        def __init__(
                self,
                appender: BaseTableAppender,
                thread_num: int
        ):
            super().__init__()
            self.appender = appender
            self.thread_num = thread_num

        def run(self):
            for _ in range(1000 // self.thread_num):
                appender.append([
                    random.random(),
                    random.choice(''.join(random.choices(string.printable, k=5))),
                    random.randint(1, 100000),
                    time.time()
                ])

    appender = load_table_appender_class(_appender_class_name)(
        "test",
        ["RAND_FLOAT", "RAND_STR", "RAND_INT", "TIME"]
    )
    ts = time.time()
    process_pool = []
    for _ in range(_thread_num):
        process_pool.append(AppenderProcess(appender, thread_num=thread_num))
        process_pool[-1].start()
    for i in range(_thread_num):
        process_pool[i].join()
    te = time.time()
    appender.close()
    if appender._real_filename != "":
        os.remove(appender._real_filename)
    _final_result_appender.append([
        _appender_class_name,
        _thread_num,
        _run_id,
        te - ts
    ])


if __name__ == '__main__':
    try:
        os.remove("bench_result.tsv")
    except FileNotFoundError:
        pass
    final_result_appender = load_table_appender_class("TSVTableAppender")(
        "bench_result",
        ["APPENDER_CLASS_NAME", "THREAD_NUM", "RUN_ID", "TIME_SPENT"]
    )
    for appender_class_name in AVAILABLE_TABLE_APPENDERS:
        for thread_num in range(1, multiprocessing.cpu_count() * 2):
            desc = f"{appender_class_name} with {thread_num} threads"
            for run_id in tqdm.tqdm(range(1000), desc=desc):
                bench_multithread(appender_class_name, thread_num, run_id, final_result_appender)
        print(f"Benchmarking {appender_class_name} FIN")
    final_result_appender.close()
