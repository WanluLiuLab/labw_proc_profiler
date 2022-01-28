#include "cst_workload.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

int perform_sqrt(int num_of_rounds, int num_to_sqrt)
{
    double *result = (double *) malloc(sizeof(double) * num_to_sqrt);
    if (result == NULL) {
        return 1;
    }
    for (int round = 0; round < num_of_rounds; round++) {
        for (int i = 0; i < num_to_sqrt; i++) {
            result[i] = sqrt(i);
        }
    }
    free(result);
    result = NULL;
    return 0;
}


parallel_params_type parse_args(int argc, char **argv)
{
    printf("Args:");
    for (int i = 0; i < argc; i++){
        printf(" %s", argv[i]);
    }
    printf("\n");
    parallel_params_type parallel_params;
    parallel_params.num_to_sqrt = atoi(argv[1]);
    parallel_params.num_of_rounds = atoi(argv[2]);
    parallel_params.num_of_threads = atoi(argv[3]);
    printf("num_to_sqrt %d\n", parallel_params.num_to_sqrt);
    printf("num_of_rounds %d\n", parallel_params.num_of_rounds);
    printf("num_of_threads %d\n", parallel_params.num_of_threads);
    return parallel_params;
}
