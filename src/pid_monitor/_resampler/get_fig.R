library(tidyverse)
library(parallel)
library(patchwork)

setwd("/home/yuzj/Documents/gpmf/opt/proc_profiler/src/pid_monitor/_test")

cl <- parallel::makeForkCluster()

get_supplementary_plot <- function(dirname) {
    MAX_X_LABS <- 60
    message(sprintf("Plotting %s...", dirname))

    d <- readr::read_csv(
        sprintf("%s/final.csv", dirname),
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
            "Metrics Value",
            breaks = scales::breaks_extended(n = 5),
            labels = scales::label_number(),
            limits = c(0, NA)
        ) +
        scale_color_discrete(name = "Metrics Type") +
        labs(title = "Metrics Values")

    ggsave(
        sprintf("%s/final.png", dirname),
        d_plot,
        width = 10,
        height = 8
    )
    return(d_plot)
}

# get_plot("flair_20")


get_required_data <- function(dirname) {
    # CPU time
    # Peak virt data
    message(sprintf("Getting required %s...", dirname))

    d <- readr::read_csv(
        sprintf("%s/final.csv", dirname),
        show_col_types = FALSE
    )

    peak_virt <- max(d$VIRT)
    peak_data <- max(d$DATA)
    mean_virt <- mean(d$VIRT)
    mean_data <- mean(d$DATA)
    cpu_time <- max(d$TIME) - mean(d$TIME)
    cpu_time <- 0.0
    for (cpu_time_filename in  Sys.glob(sprintf("%s/*.cputime", dirname))) {
        con <- file(cpu_time_filename, "r")
        cpu_time <- cpu_time + as.numeric(readLines(con, n = 1))
        close(con)
    }
    return(c(cpu_time, peak_data, peak_virt, mean_data, mean_virt))
}


flist <- c("proc_profiler_calibrate_cpu", "proc_profiler_calibrate_mem")

# plot_table <- tibble::tibble(
#     SOFT = c(),
#     DATA_SIZE = c(),
#     CPU_TIME = c(),
#     PEAK_DATA = c(),
#     PEAK_VIRT = c()
# )
# for (software in c("flair", "FLAMES", "freddie", "NanoAsPipe", "stringtie", "unagi")) {
#
#     for (depth in seq(20, 100, 20)) {
#         dirname <- paste(software, depth, sep = "_")
#         flist <- c(flist, dirname)
#
#         this_required_data <- get_required_data(dirname)
#         plot_table <- dplyr::bind_rows(
#             plot_table,
#             tibble::tibble(
#                 SOFT = software,
#                 DATA_SIZE = depth,
#                 CPU_TIME = c(this_required_data[1]),
#                 PEAK_DATA = c(this_required_data[2]),
#                 PEAK_VIRT = c(this_required_data[3]),
#                 MEAN_DATA = c(this_required_data[4]),
#                 MEAN_VIRT = c(this_required_data[5])
#             )
#         )
#     }
# }
#
# plot_table_wide <- plot_table %>%
#     dplyr::select(!(CPU_TIME)) %>%
#     tidyr::gather(key = "MEM_TYPE", value = "V", -SOFT, -DATA_SIZE)
#
# ggplot(plot_table_wide, aes(x = DATA_SIZE, y = V)) +
#     geom_bar(
#         aes(fill = SOFT),
#         stat = "identity",
#         position = "dodge"
#     ) +
#     theme_bw() +
#     scale_y_continuous(
#         "Memory Consumption",
#         breaks = scales::breaks_extended(n = 10),
#         labels = scales::label_bytes(accuracy = 0.1)
#     ) +
#     scale_fill_discrete(name = "Software Name") +
#     facet_wrap(. ~ MEM_TYPE, scales = "free_y")
#
# ggplot(plot_table, aes(x = DATA_SIZE, y = CPU_TIME)) +
#     geom_line(aes(color = SOFT)) +
#     theme_bw() +
#     scale_y_continuous(
#         "CPU Time",
#         breaks = scales::breaks_extended(n = 10),
#         labels = scales::label_number()
#     ) +
#     scale_color_discrete(name = "Software Name")
#
# ggplot(plot_table, aes(x = CPU_TIME, y = MEAN_VIRT)) +
#     geom_point(aes(color = SOFT)) +
#     theme_bw() +
#     scale_x_continuous(
#         "CPU Time",
#         breaks = scales::breaks_extended(n = 10),
#         labels = scales::label_number(),
#         trans="log"
#     ) +
#     scale_y_continuous(
#         "Mean Virtual Memory Consumption",
#         breaks = scales::breaks_extended(n = 10),
#         labels = scales::label_bytes(accuracy = 0.1),
#         trans="log"
#     ) +
#     scale_color_discrete(name = "Software Name")
#
# ggplot(plot_table, aes(x = CPU_TIME, y = PEAK_VIRT)) +
#     geom_point(aes(color = SOFT)) +
#     theme_bw() +
#     scale_x_continuous(
#         "CPU Time",
#         breaks = scales::breaks_extended(n = 10),
#         labels = scales::label_number(),
#         trans="log"
#     ) +
#     scale_y_continuous(
#         "Peak Virtual Memory Consumption",
#         breaks = scales::breaks_extended(n = 10),
#         labels = scales::label_bytes(accuracy = 0.1),
#         trans="log"
#     ) +
#     scale_color_discrete(name = "Software Name")

parSapply(cl = cl, X = flist, FUN = get_supplementary_plot)

ggplot(r, aes(x=TIME)) + geom_line(aes(y=VIRT), color="blue") + geom_line(aes(y=RESIDENT), color="red") + geom_line(aes(y=SHARED), color="black") + geom_line(aes(y=TEXT), color="green") + geom_line(aes(y=DATA), color="purple")
