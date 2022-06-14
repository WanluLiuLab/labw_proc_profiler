#!/usr/bin/env bash
# shellcheck disable=SC2002
# shellcheck disable=SC2001
find . | grep '\.py$' | while read -r line; do
    echo "${line}" | sed 's;\.py$;;' | sed 's;^\./;;' | sed 's;/;.;g'
    cat "${line}" |\
    grep -e "^import .*$" -e "^from .* import .*$" |\
    grep 'pid_monitor' |\
    grep -v '^$'
    echo
done
