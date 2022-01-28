#!/usr/bin/env bash
set -ue
SHDIR="$(dirname "$(readlink -f "${0}")")"
cd "${SHDIR}" || exit 1

cat Main.jsh.in | \
sed 's;__NUM_TO_SQRT__;'"${1:-1048576}"';' |\
sed 's;__NUM_OF_ROUNDS__;'"${2:-10240}"';' |\
sed 's;__NUM_OF_THREADS__;'"${3:-20}"';' | jshell
