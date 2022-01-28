# `proc_profiler` -- A Python-Implemented Process Profiler for GNU/Linux

```{warning}
This application is for GNU/Linux **ONLY**.
```

**Markdown Compatibility Guide**: This readme is written in MyST-Flavor Markdown. If you have problem previewing it, please download Microsoft Visual Studio Code and install a plugin with ID [ExecutableBookProject.myst-highlight](https://marketplace.visualstudio.com/items?itemName=ExecutableBookProject.myst-highlight).

## Introduction

This is `proc_profiler`, a process-level general-purposed process profiler, which may record performance of a program written in arbitrary language.

This project is considered a part of GPMF -- General Purposed Maintenance Framework, but can be distributed by itself. The execution of this project do not need GPMF, while developing and maintenance of this project requires it as a submodule of current GPMF release.

The project is built at the top of [psutil](https://psutil.readthedocs.io/en/latest/).

## Dependencies

This project is coded under Python (CPython implementation) and R, so please install its interpreters. Recommended Python version >= 3.7 and R version >= 4.0.0.

Following R packages are needed:

- `argparser`
- `ggpubr`
- `knitr`
- `rmarkdown`
- `scales`
- `tidyverse`

Following Python packages are needed:

- `psutil`
- `prettytable`
- `tqdm`

## Installation

The installation process is simple, just open a Python 3 environment and install it using pip:

```shell
python3 -m pip install proc_profiler
```

You may add this program to `requirements.txt` of your program to have it profiled.

## Documentations

## Quickstart: `proc_profiler`

`proc_profiler` is a Python module which may trace a command like `strace`. The backend of this module is `pid_monitor` introduced below.

### Using `bin/proc_profiler.sh` wrapper

SYNOPSIS: `bin/proc_profiler.sh [command]`

```{note}
This calls `setup.sh` to check and install the dependencies.
```

e.g. To trace `sleep 5`, one can execute following command:

```shell
bin/proc_profiler.sh sleep 5
```

You will get a output like:

```text
======================= Starting =======================
proc_profiler -- Process Monitor Utilities ver. 0.2
Called by: /home/yuzj/Documents/gpmf/opt/proc_profiler/src/proc_profiler/__main__.py sleep 5
Output to: proc_profiler_58d2891e-40fb-4c48-90a5-3346371a09e0
CPU%: 4.8
VIRTUALMEM: AVAIL: 40.14GiB/62.49GiB=64.23%BUFFER: 876.99MiB SHARED 54.96MiB
SWAP: AVAIL: 24.13GiB/30.76GiB=78.4% I/O: 3.19GiB/10.93GiB
+--------+--------+-------+----------+------+----------+--------------+-------------+-------------------+
|  PID   |  PPID  |  NAME |   STAT   | CPU% | CPU_TIME | RESIDENT_MEM | NUM_THREADS | NUM_CHILD_PROCESS |
+--------+--------+-------+----------+------+----------+--------------+-------------+-------------------+
| 168035 | 168033 | sleep | sleeping | 0.0  |   0.0    |   752.0KiB   |      1      |         0         |
+--------+--------+-------+----------+------+----------+--------------+-------------+-------------------+
CPU%: 5.6
Toplevel PID finished
Compiling HTMLs: 100%|======================================================| 2/2 [00:05<00:00,  2.81s/it]
```

With a log file `tracer.log` generated inside your working directory.

### Calling this profiler directly

Wish to get rid of that GPMF-style `setup.sh`? Just replace `bin/proc_profiler.sh` with `python -m proc_profiler` and do as above.

If you get a `python: No module named proc_monitor` with exit value 1, please set up the environment correctly.

## Quickstart: `pid_monitor`
