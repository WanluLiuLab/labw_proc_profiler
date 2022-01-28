# ==============================================================================
#  Copyright (C) 2021-2022. tetgs authors
#
#  This file is a part of tetgs, which is licensed under MIT,
#  a copy of which can be obtained at <https://opensource.org/licenses/MIT>.
#
#  NAME: rmd_args.R -- Public functions of RMarkdown.
#
#  VERSION HISTORY:
#  2021-09-08 0.1  : Purposed and added by YU Zhejian
#
# ==============================================================================
#' rmd_args.R -- Public functions of RMarkdown.

#' Load packages
library(tidyverse)
library(scales)
library(ggpubr)
library(knitr)

knitr::opts_chunk$set(
    echo = FALSE
    # fig.width = 16,
    # fig.height = 10
)

#' Maximun number of labels on X axis.
MAX_X_LABS <- 40

#' Generate error message for non-exist files.
print_se <- function(){
    cat("ERROR: File not exist, too short or invalid.")
}

#' Function to print a file. Will generate a error message if not exist.
#' @param filename: Filename to print
print_file <- function(filepath) {
    if (!file.exists(filepath) || file.info(filepath)$size == 0) {
        print_se()
        return()
    }
    con <- file(filepath, "r")
    while (TRUE) {
        line <- readLines(con, n = 1)
        if (length(line) == 0) {
            break
        }
        cat(line)
        cat('\n')
    }
    close(con)
}

#' Similiar to `print_file`, but print a kable.
print_kable <- function(filepath) {
    if (!file.exists(filepath)) {
        print_se()
        return()
    }
    table <- read_tsv(filepath, show_col_types = FALSE)
    if (dim(table)[1] == 0){
        print_se()
    } else {
        kable(table)
    }
}

#' Generate blocked x-axis forom levels.
generate_breaks <- function(lvls) {
    if (length(lvls) <= MAX_X_LABS) {
        breaks <- lvls
    } else {
        scale_by <- as.integer(length(lvls) / MAX_X_LABS) + 1
        breaks <- lvls[seq(1, length(lvls), by = scale_by)]
    }
    return(breaks)
}

#' Date and time type used in records
record_time_format <- "%F %H:%M:%OS" # 2022-01-09 14:54:50.16

#' Function to apply theme setetings to CPU graph
#' @param g: Graph to be applied
cpu_graph_prettify <- function(g) {
    g <- g +
        theme_bw() +
        theme(axis.text.x = element_text(angle = 90)) +
        scale_x_datetime(
            "Time",
            breaks = breaks_pretty(n = MAX_X_LABS),
            labels = label_date(format = record_time_format)
        ) +
        scale_y_continuous(
            "CPU Percent",
            limits = c(0, NA)
        ) +
        labs(title = "Mean CPU Ultilization plot")
    return(g)
}
