#include <stdio.h>
#include <omp.h>
#include "cst_workload.h"


int main(int argc, char **argv);

int main(int argc, char **argv)
{
    parallel_params_type parallel_params = parse_args(argc, argv);

#pragma omp parallel for
    for (int i = 0; i < parallel_params.num_of_threads; i++) {
        int retv;
        int thread_no = omp_get_thread_num();
        printf("Thread %d start\n", thread_no);
        retv = perform_sqrt(parallel_params.num_of_rounds, parallel_params.num_to_sqrt);
        printf("Thread %d join with return value %d\n", thread_no, retv);
    }
    return 0;

}

