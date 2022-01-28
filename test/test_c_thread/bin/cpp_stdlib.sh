#!/usr/bin/env bash
set -ue
SHDIR="$(dirname "$(readlink -f "${0}")")"
"${SHDIR}"/../src/bin/cpp_stdlib.co "${1:-1048576}" "${2:-10240}" "${3:-20}"
