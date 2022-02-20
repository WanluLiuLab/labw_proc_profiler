if(file.exists("renv/activate.R")) {
    source("renv/activate.R")
}

library(argparser)
library(rmarkdown)

p <- arg_parser("make_docker_report.R -- Make report from Docker Monitor")
p <- add_argument(p, "--basename", help = "The basename call", type = "character")
p <- add_argument(p, "--rmd", help = "The R Markdown Template", type = "character")
p <- add_argument(p, "--name", help = "Name of traced container", type = "character")

argv <- parse_args(p)
cmdline <- cat(commandArgs(), sep = ' ')
print(cmdline)

knit_root_dir <- tempdir()
render(argv$rmd,
       params = list(basename = argv$basename,
                     name = argv$name,
                     RMD_ARGS = getwd()
       ),
       output_dir = dirname(argv$basename),
       intermediates_dir = knit_root_dir,
       knit_root_dir = knit_root_dir,
       output_file = paste0("Report_", argv$name, '.html'),
)
unlink(knit_root_dir, recursive = TRUE, force = TRUE)
