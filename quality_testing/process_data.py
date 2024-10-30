from typing import Tuple, List
import numpy as np
import os
from pathlib import Path

PERCENT_RANGE_START = 0
PERCENT_RANGE_END = 1

CWD = Path(__file__).parent
RAW_DATA_DIR_PATH = os.path.join(CWD, "data/raw")


def split_by_percentages(prefix_ratio: float, snippet: str) -> Tuple[str, str]:
    if not prefix_ratio > 0 and prefix_ratio < 1:
        raise ValueError("Prefix ratio has to be a value between 0 and 1")
    split_idx = round(len(snippet) * prefix_ratio)
    return snippet[:split_idx], snippet[split_idx:]


def load_file(path: str) -> str:
    with open(path, "r") as f:
        content = f.read()
        return content


def save_file(path: str, content: str):
    with open(path, "w") as f:
        f.write(content)


def generate_split_ratios(step: float) -> list:
    prefix_percentages = np.arange(PERCENT_RANGE_START, PERCENT_RANGE_END, step)
    return prefix_percentages[1:]


def generate_split_prefixes_by_ratios(
    prefix_ratios: List[float], snippet: str
) -> List[Tuple[float, str]]:
    ratio_splits = {}
    for ratio in prefix_ratios:
        prefix, remainder = split_by_percentages(ratio, snippet)
        ratio_splits.append((ratio, prefix))
    return ratio_splits


if __name__ == "__main__":
    og_algorithm = load_file(os.path.join(RAW_DATA_DIR_PATH, "bucket_sort.py"))

    algorithm_splits = generate_split_prefixes_by_ratios(
        generate_split_ratios(0.2),
        og_algorithm,
    )
    for ratio, prefix in algorithm_splits:
        print(f"{ratio}:\n{prefix}")
