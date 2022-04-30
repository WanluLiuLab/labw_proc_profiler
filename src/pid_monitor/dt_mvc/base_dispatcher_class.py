import gc
import logging
import threading
import time
from abc import abstractmethod
from typing import Dict, Any, Iterable

from pid_monitor import DEFAULT_REFRESH_INTERVAL
from pid_monitor.dt_mvc.tracer_loader import get_tracer_class


class BaseTracerDispatcherThread(threading.Thread):
    """
    The base class of all dispatchers.
    """
    basename: str
    """The report basename."""

    dispatchee: str
    """What is being traced? PID for process, ``sys`` for system"""

    thread_pool: Dict[str, threading.Thread]
    """The tracer Thread, is name -> thread"""

    loaded_tracers: Iterable[str]
    """List[str] of loaded tracers."""

    tracer_kwargs: Dict[str, Any]
    """Dict[str,Any] for tracer options."""

    interval: float
    """Whether this thread should be terminated"""

    should_exit: bool
    """Interval of tracing in seconds."""

    def __init__(
            self,
            dispatchee: str,
            basename: str,
            interval: float = DEFAULT_REFRESH_INTERVAL
    ):
        super().__init__()
        self.log_handler = logging.getLogger()
        self.basename = basename
        self.dispatchee = dispatchee
        self.thread_pool = {}
        self.loaded_tracers = []
        self.tracer_kwargs = {"basename": self.basename}
        self.interval = interval
        self.should_exit = False

    def append_threadpool(self, thread: threading.Thread):
        self.thread_pool[thread.__class__.__name__] = thread

    def start_tracers(self):
        """Start loaded tracers. Should be called at the end of :py:func:`init`."""
        for tracer in self.loaded_tracers:
            try:
                self.log_handler.info(f"DISPATCHEE={self.dispatchee}: Fetch TRACER={tracer}")
                new_thread = get_tracer_class(tracer)(**self.tracer_kwargs)
                self.log_handler.info(f"DISPATCHEE={self.dispatchee}: Fetch TRACER={tracer} SUCCESS")
            except Exception as e:
                self.log_handler.error(
                    f"DISPATCHEE={self.dispatchee}: Fetch TRACER={tracer} {e.__class__.__name__} encountered!"
                )
                continue
            new_thread.start()
            self.log_handler.info(f"DISPATCHEE={self.dispatchee}: Start TRACER={tracer}")
            self.append_threadpool(new_thread)

    @abstractmethod
    def before_ending(self):
        """
        Method to call to perform clean exit, like writing logs.
        """
        pass

    def run(self):
        self.log_handler.info(f"Dispatcher for DISPATCHEE={self.dispatchee} started")
        self.run_body()
        self.log_handler.info(f"Dispatcher for DISPATCHEE={self.dispatchee} stopped")

    @abstractmethod
    def run_body(self):
        """
        The default runner
        """
        pass

    def __del__(self):
        """
        Force deletion.
        """
        try:
            self.sigterm()
        except AttributeError:
            pass

    def sigterm(self, *args):
        """
        Sigterm handler. By default, it:

        - Call py:func:`before_ending` method.
        - Terminate all threads in ``thread_pool``
        - Suicide.
        """
        self.log_handler.info(f"Dispatcher for DISPATCHEE={self.dispatchee} SIGTERM")
        self.before_ending()
        for thread in self.thread_pool.values():
            try:
                thread.should_exit = True
            except AttributeError:
                del thread
        time.sleep(2)
        self.thread_pool.clear()
        gc.collect()

    @abstractmethod
    def collect_information(self) -> Dict[str, Any]:
        """
        Collect process information
        """
        pass

    def __repr__(self):
        try:
            return f"Dispatcher for {self.dispatchee}"
        except AttributeError:
            return "Dispatcher under construction"

    def __str__(self):
        return repr(self)
