library(tidyverse)

df <- readr::read_tsv("bench_result.tsv", show_col_types = FALSE)

ggplot(df, aes(x=THREAD_NUM, y=TIME_SPENT)) +
    geom_violin(aes(group=THREAD_NUM, fill=THREAD_NUM)) +
    stat_summary(fun = mean, color="red", geom="line") +
    facet_grid(APPENDER_CLASS_NAME~BUFF_SIZE, scales = "free_y") +
    theme_bw()

