# ==============================================================================
#  Copyright (C) 2021-2022. tetgs authors
#
#  This file is a part of tetgs, which is licensed under MIT,
#  a copy of which can be obtained at <https://opensource.org/licenses/MIT>.
#
#  NAME: procfs_tester_multithread_multiprocess.py -- Procfs tester
#
#  VERSION HISTORY:
#  2021-08-26 0.1  : Proposed and added by YU Zhejian.
#
# ==============================================================================
"""
procfs_tester_multithread_multiprocess.py -- Procfs tester

This file will start 2 ``cat`` process with 2 Python :py:class:`threading.Thread`.
"""
import multiprocessing
import subprocess
import sys
import threading
from time import sleep

DEVZERO = open('/dev/zero')

SLEEP_TIME = 20

def process_that_does_nothing():
    return subprocess.Popen(
        ['/usr/bin/cat'],
        stdin=DEVZERO,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True
    )


class TreadThatDoesNothing(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        sleep(SLEEP_TIME)


class ProcessThatDoesNothing(multiprocessing.Process):
    def __init__(self):
        super().__init__()

    def run(self):
        sleep(SLEEP_TIME)


def main():
    print("stdout")
    print("stderr", file=sys.stderr)
    proc1 = process_that_does_nothing()  # Started on creation.
    proc2 = process_that_does_nothing()  # Started on creation.

    thread1 = TreadThatDoesNothing()
    thread2 = TreadThatDoesNothing()

    proc3 = ProcessThatDoesNothing()
    proc4 = ProcessThatDoesNothing()

    thread1.start()
    thread2.start()
    proc3.start()
    proc4.start()

    thread1.join()
    thread2.join()
    proc3.join()
    proc4.join()
    proc1.kill()
    proc2.kill()


if __name__ == '__main__':
    main()
