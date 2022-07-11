library(tidyverse)

df <- readr::read_tsv("bench_result.tsv", show_col_types = FALSE) %>%
    dplyr::mutate(THROUGHPUT=1/TIME_SPENT*1000)

p <- ggplot(df, aes(x=THREAD_NUM, y=THROUGHPUT)) +
    geom_boxplot(aes(group=THREAD_NUM), outlier.alpha=0) +
    stat_summary(fun = mean, color="red", geom="line") +
    facet_grid(APPENDER_CLASS_NAME~BUFF_SIZE, scales = "free_y") +
    theme_bw()
ggsave("a.png", p, width=10, height=12)

p <- ggplot(df, aes(x=THREAD_NUM, y=THROUGHPUT)) +
    stat_summary(aes(color=APPENDER_CLASS_NAME),fun = "mean", geom="line") +
    scale_y_continuous(trans = "log10", n.breaks = 20) +
    facet_grid(~BUFF_SIZE) +
    theme_bw()
ggsave("b.png", p, width=12, height=8)
