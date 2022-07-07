library(tidyverse)
library(parallel)
setwd("/home/yuzj/Desktop/profiler")

cl <- parallel::makeForkCluster()

MAX_X_LABS <- 60

get_plot <- function(soft) {
    message(sprintf("Plotting %s...", soft))
    d <- readr::read_csv(
        sprintf("./%s_profile/final.csv", soft),
        show_col_types = FALSE
    ) %>%
        dplyr::mutate(
            TIME = as.POSIXct(TIME, origin = "1970-01-01")
        )
    wide_d <- d %>%
        tidyr::gather(key = "MEM_TYPE", value = "V", -TIME)

    d_plot <- wide_d %>%
        ggplot() +
        geom_line(aes(x = TIME, y = V, color = MEM_TYPE)) +
        facet_grid(MEM_TYPE ~ ., scales = "free_y") +
        theme_bw() +
        scale_x_datetime(
            "Time",
            breaks = scales::breaks_pretty(n = MAX_X_LABS),
            labels = scales::label_date(format = "%Y-%m-%d %H:%M:%S")
        ) +
        theme(axis.text.x = element_text(angle = 90)) +
        scale_y_continuous(
            "Memory Allocated",
            breaks = scales::breaks_extended(n = 5),
            labels = scales::label_bytes(units = "auto_binary", accuracy = 0.01),
            limits = c(0, NA)
        ) +
        labs(title = "Mean Memory Ultilization plot")

    ggsave(
        sprintf("./%s_profile/final.png", soft),
        d_plot,
        width = 10,
        height = 8
    )
}

parSapply(cl = cl, X = c("flair", "freddie", "NanoAsPipe", "stringtie", "Tama", "unagi"), FUN = get_plot)

