#!/usr/bin/env bash
#===============================================================================
# Copyright (C) 2021-2022. gpmf authors
#
# This file is a part of gpmf, which is licensed under MIT,
# a copy of which can be obtained at <https://opensource.org/licenses/MIT>.
#
# NAME: proc_profiler.sh -- Frontend of prof_profiler
#
# VERSION HISTORY:
# 2021-10-25 0.1  : Purposed and added by YU Zhejian.
#
#===============================================================================
set -ue
SHDIR="$(dirname "$(readlink -f "${0}")")"
PROF_PROFILER_DIR="${SHDIR}/../"
bash "${PROF_PROFILER_DIR}"/setup.sh
. "${PROF_PROFILER_DIR}"/activate.sh
python3 -m proc_profiler "${@}"
