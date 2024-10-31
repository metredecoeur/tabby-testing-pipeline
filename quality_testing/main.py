import json
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
from typing import List

import process_data
import fetch_suggestions


CWD = Path(__file__).parent
RAW_DATA_DIR_PATH = os.path.join(CWD, "data/raw")
PROCESSED_DATA_DIR_PATH = os.path.join(CWD, "data/processed")
TABBY_SUGGESTIONS_DATA_DIR = os.path.join(CWD, "data/tabby-suggestions")

SPLIT_RATIO_STEP = 0.2

STRING_BASED_SIMILARITY_ALGORITHMS = {
    SequenceMatcher.__name__: lambda og, replica: SequenceMatcher(
        isjunk=None, a=og, b=replica
    ).ratio(),
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


def get_all_filenames_from_data_dir(dirpath: str) -> List[str]:
    filenames = [fpath.name for fpath in Path(dirpath).iterdir() if fpath.is_file()]
    return filenames


def main():
    # prep env
    load_dotenv()
    tabby_auth_token = os.environ["tabby_auth_token"]
    filenames = get_all_filenames_from_data_dir(RAW_DATA_DIR_PATH)
    for fname in filenames:
        testing_data = gen_algorithm_splits_and_test(fname, tabby_auth_token)
        process_data.save_file(
            os.path.join(PROCESSED_DATA_DIR_PATH, f"tested-{fname.split('.')[0]}.json"),
            json.dumps(testing_data),
        )


def gen_algorithm_splits_and_test(raw_algorithm_fname, tabby_auth_token):
    # load algorithm
    raw_algorithm = process_data.load_file(
        os.path.join(RAW_DATA_DIR_PATH, raw_algorithm_fname)
    )

    # split algorithm according to the ratio
    algorithm_splits = process_data.generate_split_prefixes_by_ratios(
        process_data.generate_split_ratios(SPLIT_RATIO_STEP),
        raw_algorithm,
    )
    # prep json data from split ratios and prefixes
    bucket_sort_data = {str(pair[0]): {"prefix": pair[1]} for pair in algorithm_splits}
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
        bucket_sort_data[str(ratio)]["choices"] = []

        for idx, choice in enumerate(suggestion["choices"]):
            tabby_completed_algorithm = prefix + choice["text"]
            process_data.save_file(
                os.path.join(
                    TABBY_SUGGESTIONS_DATA_DIR, f"tabby-gen-{idx}-{raw_algorithm_fname}"
                ),
                tabby_completed_algorithm,
            )

            algorithms_test_results = {}
            for algorithm_name, algorithm in STRING_BASED_SIMILARITY_ALGORITHMS.items():
                result = algorithm(raw_algorithm, tabby_completed_algorithm)
                algorithms_test_results[algorithm_name] = result

            bucket_sort_data[str(ratio)]["choices"].append(
                {tabby_completed_algorithm: algorithms_test_results}
            )

    return bucket_sort_data


if __name__ == "__main__":
    main()
