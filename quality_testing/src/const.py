from difflib import SequenceMatcher
from jellyfish import (
    damerau_levenshtein_distance,
    hamming_distance,
    jaro_winkler_similarity,
)

TABBY_URL = "http://localhost:8080/v1/completions"

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