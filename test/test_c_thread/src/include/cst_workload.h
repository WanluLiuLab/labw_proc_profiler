#ifdef __cplusplus
extern "C" {
#endif
int perform_sqrt(int num_of_rounds, int num_to_sqrt);

typedef struct{
    int num_to_sqrt;
    int num_of_rounds;
    int num_of_threads;
} parallel_params_type;

parallel_params_type parse_args(int argc, char **argv);

#ifdef __cplusplus
};
#endif
