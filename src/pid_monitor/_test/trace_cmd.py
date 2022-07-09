import os
import shutil

from pid_monitor.main.trace_cmd import run_process


def run_sh(script_name: str, *args):
    output_basename = os.path.join(FILE_DIR, f"proc_profiler_{script_name}_test")
    try:
        shutil.rmtree(output_basename)
    except FileNotFoundError:
        pass
    cmd = ["sh", os.path.join(SH_DIR, f"{script_name}.sh")]
    cmd.extend(args)
    run_process(
        cmd,
        output_basename
    )


if __name__ == "__main__":
    FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    SH_DIR = os.path.join(FILE_DIR, "sh")
    run_sh("dd_xz")
    run_sh("fast_fork")
