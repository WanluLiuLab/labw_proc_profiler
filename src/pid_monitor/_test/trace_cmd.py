import os
import shutil
import sys

from pid_monitor.main.trace_cmd import run_process

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
SH_DIR = os.path.join(FILE_DIR, "sh")
PY_DIR = os.path.join(FILE_DIR, "py")

def run_py(script_name: str, *args):
    output_basename = os.path.join(FILE_DIR, f"proc_profiler_{script_name}_test")
    try:
        shutil.rmtree(output_basename)
    except FileNotFoundError:
        pass
    cmd = [sys.executable, os.path.join(PY_DIR, f"{script_name}.py")]
    cmd.extend(args)
    run_process(
        cmd,
        output_basename
    )

def run_sh(script_name: str, *args):
    output_basename = os.path.join(FILE_DIR, f"proc_profiler_{script_name}_test")
    try:
        shutil.rmtree(output_basename)
    except FileNotFoundError:
        pass
    cmd = [shutil.which("bash"), os.path.join(SH_DIR, f"{script_name}.sh")]
    cmd.extend(args)
    run_process(
        cmd,
        output_basename
    )


if __name__ == "__main__":
    # run_py("calibrate_cpu")
    # run_py("calibrate_mem")
    # run_py("calibrate_cputime")
    # run_py("calibrate_disk")
    run_py("calibrate_fork_speed")
    # run_sh("dd_xz")
    # run_sh("fast_fork")
