"""
Module for aggregation and time-series analysis of results
"""
import argparse
from typing import List


def _parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--resolution",
        type=float,
        default=0.01
    )
