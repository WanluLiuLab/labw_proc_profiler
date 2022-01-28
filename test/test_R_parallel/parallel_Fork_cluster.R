library(parallel)

no_cores <- 20

cl <- makePSOCKcluster(no_cores)
source("public.R")
a <- parSapply(cl, seq(1, no_cores), worker)
stopCluster(cl)

