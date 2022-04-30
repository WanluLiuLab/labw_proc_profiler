#!/usr/bin/env bash
# Shell script that counts how many lines of code was written by us.
# shellcheck disable=SC2086
echo "Enumerating sources..."
SOURCES=$(
    git ls-files |\
    grep -v '\.maint' |\
    grep -v '\.idea' |\
    xargs
)
echo "Enumerating sources FIN"
if [ -n "${SCC:-}" ]; then
  "${SCC}" ${SOURCES}
elif which scc &>/dev/null;then
    scc ${SOURCES}
elif which cloc &>/dev/null;then
    cloc ${SOURCES}
else
    echo "scc or cloc required!"
fi
