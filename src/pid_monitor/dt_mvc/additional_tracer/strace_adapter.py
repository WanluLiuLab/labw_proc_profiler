import lzma
import re
import shutil
import subprocess
from typing import TextIO, Tuple

from pid_monitor import get_timestamp
from pid_monitor.dt_mvc.base_tracer_class import BaseProcessTracerThread

PLINE_ERR_REGEX = re.compile(r"^ = -1 (.+) \(.+\)$")
PLINE_SIGNAL_REGEX = re.compile(r"--- (.+?) .*")

__all__ = ("ProcessSyscallTracerThread",)


class ProcessSyscallTracerThread(BaseProcessTracerThread):
    # FIXME: Some error!
    def print_header(self, writer: TextIO, **kwargs):
        writer.write("\t".join((
            "TIME",
            kwargs.get('type')
        )) + "\n")

    def print_body(self, writer: TextIO, **kwargs):
        """
        This method not used.
        """
        pass

    def __init__(self, strace_path=shutil.which("strace"), **kwargs):
        super().__init__(tracer_type="strace", **kwargs)
        self.strace_path = strace_path
        if not self.strace_path:
            raise FileNotFoundError("No strace present!")

    @staticmethod
    def parse_pline(pline: str) -> Tuple[str, str, str]:
        """
        Parse strace line and return [call, err, signal]

        Plines may look like this:

            wait4(-1, [{WIFEXITED(s) && WEXITSTATUS(s) == 0}], 0, NULL) = 296026
    rt_sigaction(SIGINT, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=SA_RESTORER, sa_restorer=0x7f070d5a8910}, {sa_handler=0x55a3c6759cb0, sa_mask=[], sa_flags=SA_RESTORER, sa_restorer=0x7f070d5a8910}, 8) = 0
    ioctl(2, TIOCGWINSZ, 0x7ffce8eb16b0)    = -1 ENOTTY (Inappropriate ioctl for device)
    rt_sigprocmask(SIG_SETMASK, [QUIT], NULL, 8) = 0
    --- SIGCHLD {si_signo=SIGCHLD, si_code=CLD_EXITED, si_pid=296026, si_uid=1000, si_status=0, si_utime=2251, si_stime=4} ---
    wait4(-1, 0x7ffce8eb08d0, WNOHANG, NULL) = -1 ECHILD (No child processes)
    rt_sigreturn({mask=[QUIT]})             = 0
    read(255, "", 152)                      = 0
    rt_sigprocmask(SIG_BLOCK, [CHLD], [QUIT], 8) = 0
    rt_sigprocmask(SIG_SETMASK, [QUIT], NULL, 8) = 0
    exit_group(0)                           = ?
        """
        call = pline[0:pline.find("(")]
        if pline.startswith("---"):
            signal_match = re.match(PLINE_SIGNAL_REGEX, pline)
            if signal_match is None:
                signal = "UNPARSABLE_ERROR"
            else:
                signal = signal_match.group(1)
            return "", "", signal
        if " = -1 " in pline:
            err_raw = pline[pline.find(" = -1 "):]
            err_match = re.match(PLINE_ERR_REGEX, err_raw)
            if err_match is None:
                err = "UNPARSABLE_ERROR"
            else:
                err = err_match.group(1)
        else:
            err = "NORM"
        return call, err, ""

    def run_body(self):
        raw_out_file = f"{self.basename}.{self.trace_pid}.strace_raw.txt.xz"
        syscall_out_file = f"{self.basename}.{self.trace_pid}.strace_call.tsv"
        err_out_file = f"{self.basename}.{self.trace_pid}.strace_err.tsv"

        with subprocess.Popen((
                self.strace_path,
                "--no-abbrev",
                "-qqq",
                "-p",
                str(self.trace_pid)
        ), stderr=subprocess.PIPE) as proc:
            with lzma.open(raw_out_file, "wt", preset=9, encoding="utf-8", newline="\n") as raw_writer, \
                    open(syscall_out_file, "w") as syscall_writer, \
                    open(err_out_file, "w") as err_writer:
                self.print_header(syscall_writer, type="CALL")
                self.print_header(syscall_writer, type="ERR")
                while not self.should_exit:
                    pline = proc.stderr.readline()
                    timestamp = get_timestamp()
                    if not pline:
                        break
                    pline = str(pline, encoding="utf-8")
                    raw_writer.write("\t".join((
                        timestamp,
                        pline
                    )) + "\n")
                    call, err, signal = self.parse_pline(pline)
                    if call is not None:
                        syscall_writer.write("\t".join((
                            timestamp,
                            call
                        )) + "\n")
                    if err is not None:
                        err_writer.write("\t".join((
                            timestamp,
                            err
                        )) + "\n")
