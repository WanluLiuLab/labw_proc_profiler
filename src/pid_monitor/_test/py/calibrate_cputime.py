import math
import time

from joblib import Parallel, delayed


def workload():
    ts = time.time()
    while time.time() - ts < 10:
        _ = math.sqrt(1000)


if __name__ == "__main__":
    Parallel(n_jobs=10)(delayed(workload)() for _ in range(10))
