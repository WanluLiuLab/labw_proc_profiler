# ==============================================================================
#  Copyright (C) 2021. tetgs authors
#
#  This file is a part of tetgs, which is licensed under MIT,
#  a copy of which can be obtained at <https://opensource.org/licenses/MIT>.
#
#  NAME: setup.py -- Installer
#
#  VERSION HISTORY:
#  2021-09-11 0.1  : Purposed and added by YU Zhejian.
#
# ==============================================================================
import glob
import os.path

import setuptools
from setuptools import setup


PKG_NAME = "proc_profiler"

ROOT_DIR=os.path.dirname(__file__)

install_requires = []

with  open('requirements.txt', 'rt', encoding='utf-8') as reader:
    for line in reader:
        if not line.startswith('#'):
            install_requires.append(line.strip())

with  open('VERSION', 'rt', encoding='utf-8') as reader:
    version = reader.read()

with  open('Readme.md', 'rt', encoding='utf-8') as reader:
    long_description = reader.read()

setup(
    name=PKG_NAME,
    version=version,
    author="GPMF Authors",
    author_email="Zhejian.19@intl.zju.edu.cn",
    description="proc_profiler -- A Python-Implemented Process Profiler for GNU/Linux",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/pypa/sampleproject",  # TODO
    project_urls={  # TODO
        "Bug Tracker": "",  # TODO
        "Documentations": ""  # TODO
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: R"
    ],
    python_requires=">=3.6",
    packages=setuptools.find_packages(
        where='src',
        include=['*'],
    ),
    package_dir={"": 'src'},
    package_data ={
        '': glob.glob(os.path.join(ROOT_DIR, "src", "pid_monitor", "R", "*")),
    },
    install_requires=install_requires
)
