import subprocess
from logging import getLogger
from time import sleep

from pid_monitor._dt_mvc.pm_config import PMConfig
from pid_monitor._dt_mvc.std_dispatcher import DispatcherController

_LOGGER_HANDLER = getLogger(__name__)


def show_frontend(
        pmc: PMConfig,
        dispatcher_controller: DispatcherController
):
    """Show the frontend."""
    while len(dispatcher_controller.get_current_active_pids()) > 1:
        subprocess.call('clear')
        print(dispatcher_controller.get_frontend_cache())
        sleep(pmc.frontend_refresh_interval)
    _LOGGER_HANDLER.info("Toplevel PID finished")
