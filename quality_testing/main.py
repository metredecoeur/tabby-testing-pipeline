import os
from pathlib import Path
from dotenv import load_dotenv

from difflib import SequenceMatcher
from jellyfish import (
    levenshtein_distance,
    damerau_levenshtein_distance,
    hamming_distance,
    jaro_similarity,
    jaro_winkler_similarity,
)

import process_data
import fetch_suggestions


CWD = Path(__file__).parent
RAW_DATA_DIR_PATH = os.path.join(CWD, "data/raw")
PROCESSED_DATA_DIR_PATH = os.path.join(CWD, "data/processed")

RESULTS_FPATH = os.path.join(CWD, "combined_data.json")
SPLIT_RATIO_STEP = 0.2

STRING_BASED_SIMILARITY_ALGORITHMS = {
    SequenceMatcher.__name__: lambda og, replica: SequenceMatcher(
        isjunk=None, a=og, b=replica
    ),
    levenshtein_distance.__name__: lambda og, replica: levenshtein_distance(
        og, replica
    ),
    damerau_levenshtein_distance.__name__: lambda og, replica: damerau_levenshtein_distance(
        og, replica
    ),
    hamming_distance.__name__: lambda og, replica: hamming_distance(og, replica),
    jaro_similarity.__name__: lambda og, replica: jaro_similarity(og, replica),
    jaro_winkler_similarity.__name__: lambda og, replica: jaro_winkler_similarity(
        og, replica
    ),
}


def main():
    # prep env
    load_dotenv()
    tabby_auth_token = os.environ["tabby_auth_token"]

    # load algorithm
    original_algorithm = process_data.load_file("bucket_sort.py")

    # split algorithm according to the ratio
    algorithm_splits = process_data.generate_split_prefixes_by_ratios(
        process_data.generate_split_ratios(SPLIT_RATIO_STEP),
        original_algorithm,
    )
    # prep json data from split ratios and prefixes
    bucket_sort_data = {pair[0]: {"prefix": pair[1]} for pair in algorithm_splits}
    # get suggestions for each one of the splits
    for ratio, prefix in algorithm_splits:
        suggestion = fetch_suggestions.get_suggestion(
            fetch_suggestions.prepare_request_data(
                "python",
                prefix,
            ),
            tabby_auth_token,
        )
        # combine prefixes with suggestions
        for choice in suggestion["choices"]:
            bucket_sort_data[ratio]["choices"] = {
                choice["index"]: {"tabby_generated": prefix + choice["text"]}
            }

    # on each one of the matches for split ratio prefixes perform the string-based testing algorithms
    for ratio, prefix in algorithm_splits:
        for algorithm_name, algorithm in STRING_BASED_SIMILARITY_ALGORITHMS.items():
            for choice in bucket_sort_data[ratio]["choices"]:
                choice["index"][algorithm_name] = algorithm(
                    original_algorithm, choice["index"]["tabby_generated"]
                )

    # save results from every testing algorithm to the respective split-ratios
    process_data.save_file(RESULTS_FPATH, bucket_sort_data)
