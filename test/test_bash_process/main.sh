#!/usr/bin/env bash
set -ue
SHDIR="$(dirname "$(readlink -f "${0}")")"
cd "${SHDIR}" || exit 1

__worker(){
    echo "Process ${1} start"
    cat perform_sqrt.bc.in |\
    sed 's;__NUM_TO_SQRT__;'"${2}"';' |\
    sed 's;__NUM_OF_ROUNDS__;'"${3}"';' | bc &>> /dev/null
    echo "Process ${1} end"
}
declare -a processes
for i in $(seq 0 ${3:-20}); do
    __worker "${i}" "${1:-1048576}" "${2:-10240}" &
    processes[${i}]=${!}
done
for i in $(seq 0 ${3:-20}); do
    wait "${processes[${i}]}"
    echo "Process ${i} join"
done
