# This file is used for CLion tracking and building executables STANDALONE.
# This file should only be used if you only want to build the C part of LinuxMiniPrograms.

cmake_minimum_required(VERSION 3.9)
project(test_c_thread VERSION 1.0.0.0  LANGUAGES C CXX)

if (WIN32)
    MESSAGE(FATAL_ERROR "Platform Win32 Not Supported!")
endif()

set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 11)
add_compile_options(-Wall -Wextra -pedantic -DIS_DEBUG)
include_directories(src/include)

add_library(cst STATIC src/lib/cst_workload.c src/include/cst_workload.h)

find_package(OpenMP)

add_executable(c_openmp.co src/bin/c_openmp.c)
add_executable(c_pthread.co src/bin/c_pthread.c)
add_executable(cpp_stdlib.co src/bin/cpp_stdlib.cpp)

if(OpenMP_C_FOUND)
    target_link_libraries(c_openmp.co PUBLIC OpenMP::OpenMP_C cst)
endif()
target_link_libraries(cst m)
target_link_libraries(c_pthread.co pthread cst)
target_link_libraries(cpp_stdlib.co pthread cst)
# These libraries cannot be statically linked.
target_link_options(c_pthread.co PRIVATE -static -s)
target_link_options(cpp_stdlib.co PRIVATE -static -s)
# target_link_options(c_openmp.co PRIVATE -static -s)
