import glob
import math
import os
import re
from typing import Tuple, Optional

import pandas as pd


def get_first_and_last_timestamp_from_a_file(path: str) -> Optional[Tuple[float, float]]:
    retd_start = None
    retd_end = None
    df: pd.DataFrame
    try:
        for df in pd.read_table(path, chunksize=1000):
            if retd_start is None:
                retd_start = df['TIME'].iloc[0]
            retd_end = df['TIME'].iloc[-1]
    except (KeyError, IndexError) as e:
        return None
    if retd_start is not None:
        return retd_start, retd_end
    else:
        return None


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
            end=self.time_end,
            freq=self.interval
        )

    @classmethod
    def from_dir(cls, output_basename: str, interval: float, round_to_demical: int):
        new_instance_start = math.inf
        new_instance_end = -math.inf
        files_needed_to_be_parsed = glob.glob(os.path.join(output_basename, "*.tsv"))
        for path in files_needed_to_be_parsed:
            this_time_start_end = get_first_and_last_timestamp_from_a_file(path)
            if this_time_start_end is None:
                continue
            else:
                new_instance_start = min(new_instance_start, this_time_start_end[0])
                new_instance_end = max(new_instance_end, this_time_start_end[1])
        if new_instance_start is math.inf:
            raise ValueError(f"Failed to get valid start/end time from {output_basename}")
        return cls(
            time_start=new_instance_start,
            time_end=new_instance_end,
            interval=interval,
            round_to_demical=round_to_demical
        )


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
        print(df.head())
        df_time_start = df['TIME'][0]
        df_time_end = df['TIME'].iloc[-1]
        df_scale_start = self.rsc.index.array[self.rsc.index.array.searchsorted(df_time_start, side="right")]
        df_scale_end = self.rsc.index.array[self.rsc.index.array.searchsorted(df_time_end, side="left")]
        phase1_scale_index = pd.date_range(
            start=df_scale_start,
            end=df_scale_end,
            freq=self.rsc.interval
        )
        df = df.set_index('TIME')

        df = df.reindex(phase1_scale_index, method="bfill").reindex(self.rsc.index)
        return df


if __name__ == '__main__':
    rc = ResamplerConfig.from_dir(
        "/home/yuzj/Documents/gpmf/opt/proc_profiler/src/pid_monitor/_test/proc_profiler_test",
        1.0,
        2
    )
    print(rc.__dict__)
