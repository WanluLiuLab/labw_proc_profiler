#!/usr/bin/env Rscript
# ==============================================================================
#  Copyright (C) 2021-2022. tetgs authors
#
#  This file is a part of tetgs, which is licensed under MIT,
#  a copy of which can be obtained at <https://opensource.org/licenses/MIT>.
#
#  NAME: make_process_report.R -- Make report from Process Monitor in one Session
#
#  VERSION HISTORY:
#  2021-09-02 0.1  : Purposed and added by YU Zhejian
#
# ==============================================================================
if(file.exists("renv/activate.R")) {
    source("renv/activate.R")
}

library(argparser)
library(rmarkdown)
library(stringr)

p <- arg_parser("make_report.R -- Make report from Process Monitor")
p <- add_argument(p, "--basename", help = "The basename call", type = "character")
p <- add_argument(p, "--rmd", help = "The R Markdown Template", type = "character")

argv <- parse_args(p)
cmdline <- cat(commandArgs(), sep = ' ')
print(cmdline)

knit_root_dir <- tempdir()

pattern <- paste0("^", basename(basename), "\\.([0-9]+)\\..+")

pids <- dir(dirname(path = getwd()), pattern=pattern) %>%
    sub(pattern=pattern, replacement="\\1") %>%
    unique()

# render(argv$rmd,
#        params = list(basename = argv$basename,
#                      pid = argv$pid,
#                      RMD_ARGS = getwd()
#        ),
#        output_dir = dirname(argv$basename),
#        intermediates_dir = knit_root_dir,
#        knit_root_dir = knit_root_dir,
#        output_file = paste0("Report_", argv$pid, '.html'),
# )
# unlink(knit_root_dir, recursive = TRUE, force = TRUE)




