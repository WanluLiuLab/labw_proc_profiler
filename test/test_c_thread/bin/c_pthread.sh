#!/usr/bin/env bash
set -ue
SHDIR="$(dirname "$(readlink -f "${0}")")"
cd "${SHDIR}" || exit 1
"${SHDIR}"/../src/bin/c_pthread.co "${1:-1048576}" "${2:-10240}" "${3:-20}"
