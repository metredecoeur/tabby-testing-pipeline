from pathlib import Path
from difflib import SequenceMatcher
from jellyfish import (
    damerau_levenshtein_distance,
    hamming_distance,
    jaro_winkler_similarity,
)

TABBY_URL = "http://localhost:8080/v1/completions"
REQUESTS_TIMEOUT = 30

SPLIT_RATIO_STEP = 0.1

DEFAULT_LANGUAGE = "python"

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

LEN_RATIO_COLOR = "teal"

METRICS = [
    "cyclomatic_complexity",
    "halstead_effort",
    "halstead_bugs",
]

METRICS_PLOT_COLORS = {
    "cyclomatic_complexity": "navy",
    "halstead_effort": "orange",
    "halstead_bugs": "red",
}

PLOT_COLORS_ALPHA = 0.03
