#!/usr/bin/env bash
#===============================================================================
# Copyright (C) 2021-2022. gpmf authors
#
# This file is a part of gpmf, which is licensed under MIT,
# a copy of which can be obtained at <https://opensource.org/licenses/MIT>.
#
# NAME: setup.sh -- Make environment for this program
#
# VERSION HISTORY:
# 2021-10-25 0.1  : Purposed and added by YU Zhejian.
#
#===============================================================================
echo "======================= Starting ======================="
set -ue
SHDIR="$(dirname "$(readlink -f "${0}")")"
cd "${SHDIR}" || exit 1
[ -f "activate.sh" ] && exit 0
# FIXME: Bugs
#while [ "${CONDA_SHLVL:-0}" != "0" ]; do
#    conda deactivate
#done
#while [ -n "${VIRTUAL_ENV:-}" ];do
#    deactivate
#done

echo "======================= Locating Python3 ======================="
PATH_PYTHON_EXE="${PYTHON:-python3}"
which "${PATH_PYTHON_EXE}" || exit 1

echo "======================= Creating Python3 venv ======================="
PYTHON_VIRTUALENV_DIR="${SHDIR}/.virtualenv"
if [ ! -d "${PYTHON_VIRTUALENV_DIR}" ]; then
    "${PATH_PYTHON_EXE}" -m virtualenv "${PYTHON_VIRTUALENV_DIR}"
fi
. "${PYTHON_VIRTUALENV_DIR}"/bin/activate
PATH_PYTHON_EXE="$(which python3)"
"${PATH_PYTHON_EXE}" -m pip install -r requirements.txt

echo "======================= Locating R & renv ======================="
PATH_R_EXE="$(which R)"
echo "library(renv)" | "${PATH_R_EXE}" --vanilla

echo "======================= Creating R renv ======================="
echo "renv::init()" | "${PATH_R_EXE}" --vanilla || true

cat activate.sh.in | sed "s;__REPLACE_PROC_PROFILER_ENV_ABSPATH__;$(echo "${SHDIR}");g" > activate.sh
