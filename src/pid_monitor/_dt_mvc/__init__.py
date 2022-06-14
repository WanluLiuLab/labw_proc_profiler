import psutil

PSUTIL_NOTFOUND_ERRORS = (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied, psutil.Error)
"""Some common psutil errors."""

DEFAULT_SYSTEM_INDICATOR_PID = -1
