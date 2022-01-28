worker <- function (thread_id){
    message(sprintf("Thread %d start\n", thread_id))
    replicate(10240, {
        tmpr <- sapply(seq(1, 1048576), sqrt)
        rm(tmpr)
        NULL
    })
    message(sprintf("Thread %d end\n", thread_id))
}
