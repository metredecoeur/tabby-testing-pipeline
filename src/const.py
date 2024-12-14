from difflib import SequenceMatcher
from jellyfish import (
    damerau_levenshtein_distance,
    hamming_distance,
    jaro_winkler_similarity,
)
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = ROOT_DIR / "data/raw"
PRE_SORTED_DATA_DIR = ROOT_DIR / "data/pre-sorted"
TABBY_SUGGESTIONS_DATA_DIR = ROOT_DIR / "data/tabby-suggestions"


TABBY_URL = "http://localhost:8080/v1/completions"
REQUESTS_TIMEOUT = 30

SIMILARITY_ALGORITHMS = {
    SequenceMatcher.__name__: lambda og, replica: SequenceMatcher(
        isjunk=None, a=og, b=replica
    ).ratio(),
    damerau_levenshtein_distance.__name__: lambda og, replica: damerau_levenshtein_distance(
        og, replica
    ),
    hamming_distance.__name__: lambda og, replica: hamming_distance(og, replica),
    jaro_winkler_similarity.__name__: lambda og, replica: jaro_winkler_similarity(
        og, replica
    ),
}

ALGORITHMS_PLOT_COLORS = {
    SequenceMatcher.__name__: "brown",
    damerau_levenshtein_distance.__name__: "green",
    hamming_distance.__name__: "purple",
    jaro_winkler_similarity.__name__: "blue",
}

PLOT_COLORS_ALPHA = 0.1
