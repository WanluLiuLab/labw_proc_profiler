#!/usr/bin/env bash
dd if=/dev/random of=/dev/stdout count=10K bs=4K | xz -9 -T0 -vv -c -f > /dev/null
