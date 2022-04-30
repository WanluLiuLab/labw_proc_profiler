"""
TODO
"""

import os
import signal
import sys
import uuid
from typing import List, Optional

import docker
from docker.errors import APIError, NotFound
from docker.models.containers import Container

__version__ = 0.1

from docker_profiler.tracer import DockerDispatcherThread

client = docker.from_env()

_MONITORED_CONTAINER: Container = None


def run_container(
        image_name: str,
        output_basename: str,
        args: Optional[List[str]] = None,
        volume_str: Optional[List[str]] = None
) -> int:
    global _MONITORED_CONTAINER
    try:
        _MONITORED_CONTAINER = client.containers.run(
            image=image_name,
            volumes=volume_str,
            command=" ".join(args),
            detach=True,
            tty=False
        )
    except (APIError, NotFound):
        return 2
    try:
        dispatcher = DockerDispatcherThread(
            trace_container_name=_MONITORED_CONTAINER.name,
            basename=output_basename
        )
    except (APIError, NotFound):
        return 2
    dispatcher.start()
    dispatcher.join()

    try:
        retv = _MONITORED_CONTAINER.wait()['StatusCode']
    except (APIError, NotFound):
        return 2
    # _MONITORED_CONTAINER.remove()
    return retv


def main(
        image_name: str,
        args: Optional[List[str]] = None,
        volume_str: Optional[List[str]] = None
) -> int:
    """
    :param args: The command-line passed to this module. Should be a list of strings.
                 If not provided, will use `sys.argv[1:]`.
    :return: The return value of ``args``.
    """
    if os.environ.get('SPHINX_BUILD') == 1:
        return 0
    for _signal in (
            signal.SIGINT,
            signal.SIGTERM,
            signal.SIGHUP,
            signal.SIGABRT,
            signal.SIGQUIT,
    ):
        signal.signal(_signal, _pass_signal_to_monitored_container)

    print(f'{__doc__.splitlines()[1]} ver. {__version__}')
    print(f'Called by: {" ".join(sys.argv)}')

    output_basename = 'docker_profiler_' + str(uuid.uuid4())
    os.mkdir(output_basename)
    print(f'Output to: {output_basename}')
    return run_container(
        image_name=image_name,
        output_basename=output_basename,
        args=args,
        volume_str=volume_str
    )


def _pass_signal_to_monitored_container(signal_number: int, *_args):
    global _MONITORED_CONTAINER
    if _MONITORED_CONTAINER is None:
        pass
    try:
        _MONITORED_CONTAINER.kill(signal_number)
    except APIError:
        pass
