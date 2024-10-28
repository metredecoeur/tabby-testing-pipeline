from typing import Tuple

def split_by_percentages(prefix_ratio: float, snippet: str) -> Tuple[str, str]:
    if not prefix_ratio > 0 and prefix_ration < 1:
        raise ValueError("Prefix ratio has to be a value between 0 and 1")
    split_idx = round(len(snippet) * prefix_ratio)
    return snippet[:split_idx], snippet[split_idx:]

