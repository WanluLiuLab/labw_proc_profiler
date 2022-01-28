library(snow)
no_cores <- 20

cl <- makeSOCKcluster(replicate(no_cores, "localhost"))
source("public.R")
a <- parSapply(cl, seq(1, no_cores), worker)
stopCluster(cl)
