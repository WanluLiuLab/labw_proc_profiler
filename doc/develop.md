# Developers' Guide for `proc_profiler`

## Structure

- The main source code of this project is located in `src`, with adapters in `bin`.
- Examples of multi-threaded or multi-process programs for benchmark purpose written in C, Python and other languages are located at `test`.
- Sourcecode of the documentations are located in `doc`. For compiling documentations for local use, see documentations inside `doc`. This requires GPMF.

## Set Up the Environment


### Using GPMF `setup.sh`

All third-party libraries are automatically installed once you execute `setup.sh` except following base packages:

- Needed Python dependencies: [virtualenv](https://pypi.org/project/virtualenv/).
- Needed R dependencies: [renv](https://rstudio.github.io/renv/).

Please execute `bash setup.sh` to set up the environment.

```{note}
There's no need to call `activate.sh` unless you're a developer.
```

### Manually

On POSIX-compliant systems, R library dependencies can be searched using following command:

```shell
find src -name *.R | xargs cat  | grep ^library | sort | uniq | sed 's;library(\(.*\));\1;'
```

which gives:

```text
argparser
ggpubr
knitr
rmarkdown
scales
tidyverse
```

You may install them using `renv`, Conda or other methods. Make sure to create `renv` folder to disable `setup.sh`. The list of version in testing machine can be found at `installed-packages-and-versions-2022-01-18.R.csv`.

Python dependencies are listed in `requirements.txt`. You may install them using `venv`, `virtualenv`, Conda or other methods. Make sure to create `.virtualenv` folder to disable `setup.sh`. 

## API Reference

```{toctree}
:caption: 'Contents:'
:glob:
:maxdepth: 2

_apidoc/proc_profiler
_apidoc/pid_monitor
```
