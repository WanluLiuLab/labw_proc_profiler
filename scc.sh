#!/usr/bin/env bash
# Shell script that counts how many lines of code was written by us.
# shellcheck disable=SC2086

#!/usr/bin/env bash
#===============================================================================
# Copyright (C) 2021. tetgs authors
#
# This file is a part of tetgs, which is licensed under MIT,
# a copy of which can be obtained at <https://opensource.org/licenses/MIT>.
#
# NAME: repo_info.sh -- Generate repository information.
#
# VERSION HISTORY:
# 2021-07-15 0.1  : Purposed and added by YU Zhejian, support last commit only.
# 2021-08-17 0.1  : Author commits, names and e-mail information added.
# 2021-08-19 0.1  : Author add/delete information added. Cdde line count added.
#
#===============================================================================


builtin set -ue
NAME="repo_info.sh"
VERSION=0.1

# SHDIR="$(dirname "$(readlink -f "${0}")")"

LAST_COMMIT=$(git log --pretty=oneline --abbrev-commit --graph --branches -n 1)
AUTHOR_INFO=$(git shortlog --numbered --summary --email)
AD_MINUS=$(git log --numstat --pretty="%an$(echo -e "\t")%H" | \
    awk '
    BEGIN{
        FS="\t"
    }
    {
        if (NF == 2){
            name = $1
        };
        if(NF == 3) {
            plus[name] += $1; minus[name] += $2
        }
    }
    END {
        for (name in plus) {
            print name":\t+"plus[name]"\t-"minus[name]
        }
    }' | \
    sort -k2 -gr | \
    sed 's;^;\t;'
)

SOURCES=$(
    git ls-files |\
    grep -v '\.maint' |\
    grep -v '\.idea' |\
    xargs
)
echo "Enumerating sources FIN"
if [ -n "${SCC:-}" ]; then
    CLOC_INFO=$("${SCC}" ${SOURCES})
elif which scc &>/dev/null;then
    CLOC_INFO=$(scc ${SOURCES})
elif which cloc &>/dev/null;then
    CLOC_INFO=$(cloc ${SOURCES})
else
    echo "scc or cloc required!"
fi


cat << EOF
${NAME} ver. ${VERSION}
Called by: ${0} ${*}
Repository version information:
	The last commit is: ${LAST_COMMIT}
Author Information:
${AUTHOR_INFO}
Author changes:
${AD_MINUS}
Code count:
${CLOC_INFO}
EOF

builtin exit 0
