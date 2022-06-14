import os
import shutil

from pid_monitor.main.trace_cmd import run_process

if __name__ == "__main__":
    try:
        shutil.rmtree("proc_profiler_test")
    except FileNotFoundError:
        pass
    try:
        os.remove("tracer.log")
    except FileNotFoundError:
        pass
    run_process(
        ["sh", "-c", "dd if=/dev/random of=/dev/stdout count=10K bs=4K | xz -9 -T0 -vv -c -f > /dev/null"],
        "proc_profiler_test"
    )
