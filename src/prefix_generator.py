import numpy as np
import os
from pathlib import Path

PERCENT_RANGE_START = 0
PERCENT_RANGE_END = 1


class PrefixGenerator:
    """
    Generator for prefixes of text by given percentage step
    """

    def __init__(self, content, split_ratio_step: float):
        self._content = content
        self._check_and_set_ratio_in_range(split_ratio_step)

    def _check_and_set_ratio_in_range(self, ratio: float):
        """
        Ensure ratio in the correct range
        """
        if PERCENT_RANGE_START < ratio < PERCENT_RANGE_END:
            self._split_ratio_step = ratio
        else:
            raise ValueError(
                f"Split ratio has to be a value between {PERCENT_RANGE_START} and {PERCENT_RANGE_END}"
            )

    def next_prefix(self) -> tuple[float, str, str]:
        for ratio in np.arange(
            PERCENT_RANGE_START, PERCENT_RANGE_END, self._split_ratio_step
        )[1:]:
            yield ratio, *self._split_by_ratio(ratio)

    def _split_by_ratio(self, ratio: float) -> tuple[str, str]:
        """
        Split content by given ratio
        """
        split_idx = round(len(self._content) * ratio)
        return self._content[:split_idx], self._content[split_idx:]
