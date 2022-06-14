from typing import List

from pid_monitor._dt_mvc.appender import list_table_appender


def main(_: List[str]):
    for appender in list_table_appender():
        print(": ".join(appender))
    return 0
