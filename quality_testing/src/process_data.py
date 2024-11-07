from typing import Tuple, List
import numpy as np
import os
from pathlib import Path

PERCENT_RANGE_START = 0
PERCENT_RANGE_END = 1


def split_by_percentages(prefix_ratio: float, snippet: str) -> Tuple[str, str]:
    if not prefix_ratio > 0 and prefix_ratio < 1:
        raise ValueError("Prefix ratio has to be a value between 0 and 1")
    split_idx = round(len(snippet) * prefix_ratio)
    return snippet[:split_idx], snippet[split_idx:]




def generate_percentages_by_step(step: float) -> List[float]:
    prefix_percentages = np.arange(PERCENT_RANGE_START, PERCENT_RANGE_END, step)
    return prefix_percentages[1:]


def generate_split_prefixes_by_percentage_ratios(
        snippet: str, prefix_ratios: List[float]
) -> List[str]:
    ratio_splits = []
    for ratio in prefix_ratios:
        prefix, _ = split_by_percentages(ratio, snippet)
        ratio_splits.append(prefix)
    return ratio_splits
