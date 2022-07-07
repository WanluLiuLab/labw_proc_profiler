"""
WARNING! This file is subject to change.
"""

import glob
import math
import multiprocessing
import os
import queue
import re
import logging
from typing import Tuple, Optional, List

import pandas as pd
import tqdm

from pid_monitor._lib import parallel_helper


def get_first_and_last_timestamp_from_a_file(path: str) -> Optional[Tuple[float, float]]:
    _lh = logging.getLogger()
    _lh.debug(f"Parsing {path}")
    retd_start = None
    retd_end = None
    df: pd.DataFrame
    try:
        for df in pd.read_table(path, chunksize=1000):
            if retd_start is None:
                retd_start = df['TIME'].iloc[0]
            retd_end = df['TIME'].iloc[-1]
    except (KeyError, IndexError) as e:
        _lh.error(f"Parsing {path} error: {e} File is empty?")
        return None
    except pd.errors.ParserError as e:
        _lh.error(f"Parsing {path} error: {e}")
        return None
    if retd_start is not None:
        _lh.debug(f"Parsing {path} FIN")
        return retd_start, retd_end
    else:
        _lh.error(f"Parsing {path} error: File is empty?")
        return None


class GetFirstAndLastTimestampFromAFileProcess(multiprocessing.Process):
    def __init__(self, path: str, result_queue: multiprocessing.Queue):
        super().__init__()
        self.path = path
        self.result_queue = result_queue

    def run(self) -> None:
        self.result_queue.put(
            get_first_and_last_timestamp_from_a_file(self.path)
        )


class ResamplerConfig:
    interval: pd.Timedelta
    time_start: pd.Timestamp
    time_end: pd.Timestamp
    index: pd.DatetimeIndex

    def __init__(
            self,
            interval: float,
            time_start: float,
            time_end: float,
            round_to_demical: int
    ):
        self.interval = pd.Timedelta(interval, unit="s")
        self.time_start = pd.Timestamp(round(time_start, round_to_demical), unit="s")
        self.time_end = pd.Timestamp(round(time_end, round_to_demical), unit="s")
        self.index = pd.date_range(
            start=self.time_start,
            end=self.time_end + 2 * self.interval,
            freq=self.interval
        )

    @classmethod
    def from_dir(
            cls,
            output_basename: str,
            interval: float,
            round_to_demical: int,
            file_mask: str
    ):
        new_instance_start = math.inf
        new_instance_end = -math.inf
        files_needed_to_be_parsed = list(glob.glob(os.path.join(output_basename, file_mask)))
        manager = multiprocessing.Manager()
        result_queue = manager.Queue()
        pool = parallel_helper.ParallelJobQueue("Parsing...", refresh_interval=0, pool_size=1000)
        for path in files_needed_to_be_parsed:
            if path.find("sys") != -1:
                continue
            if path.find("resampled") != -1:
                continue
            if path.find("final") != -1:
                continue
            pool.append(GetFirstAndLastTimestampFromAFileProcess(path, result_queue))
        pool.start()
        while not pool.all_finished:
            try:
                this_time_start_end = result_queue.get(timeout=0.1)
            except (TimeoutError, queue.Empty):
                continue
            if this_time_start_end is None:
                continue
            else:
                new_instance_start = min(new_instance_start, this_time_start_end[0])
                new_instance_end = max(new_instance_end, this_time_start_end[1])
        pool.join()
        manager.shutdown()
        if new_instance_start is math.inf or new_instance_end is math.inf:
            raise ValueError(f"Failed to get valid start/end time from {output_basename}")
        new_instance = cls(
            time_start=new_instance_start,
            time_end=new_instance_end,
            interval=interval,
            round_to_demical=round_to_demical
        )
        # print(
        #     f"TS: {datetime.datetime.fromtimestamp(new_instance_start)} "
        #     f"TE: {datetime.datetime.fromtimestamp(new_instance_end)} "
        #     f"LEN: {len(new_instance.index)}"
        # )
        return new_instance


class BaseResampler:
    filename_regex: re.Pattern
    rsc: ResamplerConfig

    def __init__(
            self,
            rsc: ResamplerConfig
    ):
        self.rsc = rsc

    def resample(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        The Default resampler will resample all data
        """
        df['TIME'] = pd.to_datetime(df['TIME'], unit="s")
        if df.shape[0] == 0:
            df = df.set_index('TIME').reindex(self.rsc.index, method="bfill").reset_index(drop=False)
        else:
            df_time_start = df['TIME'][0]
            df_time_end = df['TIME'].iloc[-1]

            df_scale_start = self.rsc.index.array[self.rsc.index.array.searchsorted(df_time_start, side="right")]
            df_scale_end = self.rsc.index.array[self.rsc.index.array.searchsorted(df_time_end, side="left")]
            phase1_scale_index = pd.date_range(
                start=df_scale_start,
                end=df_scale_end,
                freq=self.rsc.interval
            )
            df = (
                df
                .set_index('TIME')
                .reindex(phase1_scale_index, method="bfill")
                .reindex(self.rsc.index)
                .reset_index(drop=False)
            )
        df['TIME'] = (df['index'] - pd.Timestamp("1970-01-01")) / pd.Timedelta("1s")  # .apply(lambda x: x.timestamp())
        df = df.drop('index', axis=1)
        # print(dict(df.dtypes))
        # print(df.head(2))
        # exit()

        return df


def aggregate_using_sum(output_basename: str, file_mask: str):
    files_needed_to_be_parsed = list(glob.glob(os.path.join(output_basename, file_mask)))
    full_df = None
    full_df_names = []
    for path in tqdm.tqdm(files_needed_to_be_parsed, desc="Aggregating..."):
        df = pd.read_parquet(path).set_index("TIME").fillna(value=0)
        # print(df.head(2))
        if full_df is None:
            full_df = df
            full_df_names = full_df.columns
            full_df = full_df.assign(NPROC=0)
        else:
            # print(full_df.head(2))
            # print(list(df.index.array))
            for time in full_df.index.array:
                if df.loc[time, full_df_names[0]] != 0:
                    full_df.loc[time, "NPROC"] += 1
            full_df = full_df.join(df, on="TIME", lsuffix="_L", rsuffix="_R")
            # print(full_df.shape)
            for name in full_df_names:
                full_df[name] = full_df[[f"{name}_L", f"{name}_R"]].sum(axis=1)
                full_df = full_df.drop([f"{name}_R", f"{name}_L"], axis=1)
                # print(full_df.dtypes.keys())
    return full_df


def parallel_resample(
        output_basename: str,
        rsc: ResamplerConfig,
        file_mask: str,
        keepfield: List[str]
):
    class ResampleProcess(multiprocessing.Process):
        def __init__(self, _rsc: ResamplerConfig, _path: str, _keepfield: List[str]):
            super().__init__()
            self.rsc = _rsc
            self.path = _path
            self.keepfield = _keepfield
            self.keepfield.append("TIME")

        def run(self) -> None:
            df = pd.read_csv(self.path, delimiter="\t", engine="pyarrow")
            for field in df.columns:
                if field not in self.keepfield:
                    df = df.drop(field, axis=1)
            (
                BaseResampler(self.rsc)
                .resample(df)
                .to_parquet(self.path.replace(".tsv", ".resampled.parquet"))
            )

    files_needed_to_be_parsed = list(glob.glob(os.path.join(output_basename, file_mask)))
    pool = parallel_helper.ParallelJobQueue(pool_name="Resampling", refresh_interval=0, pool_size=1000)
    for path in files_needed_to_be_parsed:
        if path.find("sys") != -1:
            continue
        pool.append(ResampleProcess(rsc, path, keepfield))
    pool.start()
    pool.join()


def total_process(output_basename:str):
    # print(output_basename)
    rsc = ResamplerConfig.from_dir(
        output_basename=output_basename,
        interval=1,
        round_to_demical=0,
        file_mask="*.tsv"
    )
    parallel_resample(output_basename, rsc, "*.mem.tsv", keepfield=["VIRT", "DATA"])
    parallel_resample(output_basename, rsc, "*.cpu.tsv", keepfield=["CPU_PERCENT"])
    full_df_mem = aggregate_using_sum(output_basename, "*.mem.resampled.parquet")
    full_df_cpu = aggregate_using_sum(output_basename, "*.cpu.resampled.parquet")
    full_df = full_df_mem.join(full_df_cpu, on="TIME", lsuffix="_L", rsuffix="_R")
    full_df["NPROC"] = full_df[[f"NPROC_L", f"NPROC_R"]].mean(axis=1)
    full_df = full_df.drop([f"NPROC_R", f"NPROC_L"], axis=1)
    full_df.to_csv(os.path.join(output_basename, "final.csv"))



if __name__ == '__main__':
    pool = parallel_helper.ParallelJobQueue()
    for output_basename in (
            '/home/yuzj/Documents/gpmf/opt/proc_profiler/src/pid_monitor/_test/proc_profiler_test',
            '/home/yuzj/Desktop/profiler/flair_profile/',
            '/home/yuzj/Desktop/profiler/freddie_profile/',
            '/home/yuzj/Desktop/profiler/NanoAsPipe_profile/',
            '/home/yuzj/Desktop/profiler/stringtie_profile/',
            '/home/yuzj/Desktop/profiler/Tama_profile/',
            '/home/yuzj/Desktop/profiler/unagi_profile/'
    ):
        pool.append(multiprocessing.Process(target=total_process, kwargs={"output_basename":output_basename}))
    pool.start()
    pool.join()
        # print(full_df.head())
        # sns.lineplot(data=full_df).get_figure().savefig(os.path.join(output_basename, "final_aggregated_mem.png"))
        # print(os.path.join(output_basename, "final_aggregated_mem.png"))
