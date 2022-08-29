import multiprocessing
import time


class SleepProcess(multiprocessing.Process):
    def __init__(self, n_sleep:float):
        super().__init__()
        self.n_sleep = n_sleep

    def run(self):
        time.sleep(self.n_sleep)


def fork_n(n_proc:int, n_sleep:float):
    proc_list = []
    for _ in range( n_proc):
        proc_list.append(SleepProcess(n_sleep))
        proc_list[-1].start()
    for _ in range(n_proc):
        proc_list.pop().join()

if __name__ == '__main__':
    for _n_sleep in [
        0.01,
        0.02,
        0.05,
        0.1,
        0.2,
        0.5,
        1,
        2,
        5,
        10
    ]:
        print(_n_sleep)
        fork_n(n_proc=100, n_sleep=_n_sleep)
        time.sleep(5)
