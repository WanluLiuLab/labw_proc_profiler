# Users' Guide for `proc_profiler`

## Profiling a System Benchmark

This profiler can be benchmarked by following commands:

### CPU Stress

Most programs in `test` is CPU stressing.

You may also stress CPU using `stress`. For example, use `stress --cpu 8` to benchmark with 8 cpus.

### Disk IO

You may also use `stress` with `--hdd` option. More tools are listed as follows:

`fio` with 4k random read, write, read+write using 8 threads:

```shell
mkdir -p fio_data
fio -directory="${PWD}"/fio_data/ -name=tempfile.dat -direct=1 -rw=randwrite -bs=4k -size=1M -numjobs=8 -thread -time_based -runtime=100 -group_reporting
fio -directory="${PWD}"/fio_data/ -name=tempfile.dat -direct=1 -rw=randread -bs=4k -size=1M -numjobs=8 -thread -time_based -runtime=100 -group_reporting
fio -directory="${PWD}"/fio_data/ -name=tempfile.dat -direct=1 -rw=randrw -bs=4k -size=1M -numjobs=8 -thread -time_based -runtime=100 -group_reporting
```
