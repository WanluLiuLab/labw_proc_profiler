#!/usr/bin/env bash
set -ueo pipefail

for i in {1..1000}; do
    sleep 0.1 &
done
wait
