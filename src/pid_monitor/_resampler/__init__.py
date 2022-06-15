import re
from abc import abstractmethod


class ResamplerConfig:
    interval: float
    time_start: float
    time_end: float

    def __init__(
            self,
            interval: float,
            time_start: float,
            time_end: float
    ):
        self.interval=interval
        self.time_start=time_start
        self.time_end=time_end


    @classmethod
    def from_dir(cls):
        pass




class BaseResampler:
    filename_regex: re.Pattern
    rsc:ResamplerConfig

    def __init__(
            self,
            rsc:ResamplerConfig
    ):
        self.rsc=rsc

    @abstractmethod
    def resample(self):
        pass
