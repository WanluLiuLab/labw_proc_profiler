# Testing Parallelized Applications using `test`

Here are some testing programs created by different programming languages. They may be multi-thread or multi-processed programs.

## Description

The workload accepts 3 arguments. For simplicity, I will refer to them as `$1` `$2` and `$3`. The workload will calculate square root for number from 0 to `$1` for `$2` times in `$3` subprocesses/threads/co-routines. On a system with Intel Core i9-10980XE, recommended value is 1048576, 10240 and 20.

A program should have adapters written in Shell that requires GNU Bash >= 4.4.. You may find them at:

- `bin/` directory, like `test_c_thread/bin/c_openmp.sh`.
- A file named `main.sh`, like `test_java_thread/main.sh`.

Using Shell adapters are encouraged.

## Example: Test multithreading programs written in C using `pthread`

Firstly, build these projects:

```shell
make -C test_c_thread/
```

Execute using default args:

```shell
bash test_c_thread/bin/c_pthread.sh
```

With 1024 to sqrt for 409600 rounds using 5 threads:

```shell
bash test_c_thread/bin/c_pthread.sh 1024 409600 5
```

You may get an output like:

```text
Args: ${PWD}/test/test_c_thread/bin/../src/bin/c_pthread.co 1024 409600 5
num_to_sqrt 1024
num_of_rounds 409600
num_of_threads 5
Thread 0 start
Thread 1 start
Thread 2 start
Thread 3 start
Thread 4 start
Thread 2 end with return value 0
Thread 3 end with return value 0
Thread 0 end with return value 0
Thread 0 join with return value 0
Thread 1 end with return value 0
Thread 1 join with return value 0
Thread 2 join with return value 0
Thread 3 join with return value 0
Thread 4 end with return value 0
Thread 4 join with return value 0
```

## Sub-Directories

- `test_bash_process` have programs written in Shell script. It requires GNU Bash >= 4.4 and POSIX Bash Calculator (`bc`).
- `test_java_thread` tests `Thread` class in Java >= 1.8 (aka. 8).
- `test_jshell_thread` is a JShell version of `test_java_thread`. It requires Jshell >= 9.
- `test_R_parallel` uses `snow` and `parallel` library of GNU R.
- `test_c_thread` uses pthread and openMP for C and `std::Thread` for C++. It requires:
  - A compiler that may compile openMP, like Intel dpcpp, LLVM Clang with libomp-dev or GCC with libgomp.
  - C99 and C++11 support.
  - GNU Make with GNU libtool, or CMake for building the program. This project rejects BSD make.

