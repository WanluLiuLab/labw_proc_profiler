import shutil

from pid_monitor.main.trace_cmd import run_process

if __name__ == "__main__":
    output_basename = "proc_profiler_test"
    try:
        shutil.rmtree(output_basename)
    except FileNotFoundError:
        pass

    run_process(
        ["sh", "-c", "dd if=/dev/random of=/dev/stdout count=10K bs=4K | xz -9 -T0 -vv -c -f > /dev/null"],
        output_basename
    )
