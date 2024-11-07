import argparse
import json
import os
import requests
import time
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

from typing import List

import const
import utils
import process_data
from pprint import pprint
from api_connection import TabbyConnection


CWD = Path(__file__).parent
TESTED_DATA_DIR_PATH = CWD.parent / "data/tested"
TABBY_SUGGESTIONS_DATA_DIR = CWD.parent / "data/tabby-suggestions"


def cli_arguments() -> dict:
    parser = argparse.ArgumentParser(
        prog="",
        description="",
    )

    parser.add_argument(
        "preprocessed_dir_path",
        help=f"Path to the preprocessed database to be tested, relative to {__file__}",
    )

    parser.add_argument(
        "split_ratio_step",
        help="Float: step's value for the prefix percentage split of the algorithm",
    )

    args = parser.parse_args()

    # check dir exists
    # check split in the right range

    return Path(args.preprocessed_dir_path), float(args.split_ratio_step)


def main():
    load_dotenv()
    tabby_auth_token = os.environ["tabby_auth_token"]
    session = TabbyConnection(const.TABBY_URL, tabby_auth_token)
    dir_path, split_step = cli_arguments()

    filepaths = [fpath for fpath in dir_path.rglob("*") if fpath.is_file()]

    for fpath in filepaths:
        pprint(
            f"Started: {fpath.parent.name}/{fpath.name} : {datetime.now().strftime("%H:%M")}"
        )
        percentage_ratios = process_data.generate_percentages_by_step(split_step)

        og_algorithm = utils.load_file(fpath)
        prefix_completions = generate_algorithm_splits_completions(
            og_algorithm, percentage_ratios, session
        )

        utils.save_file(
            TABBY_SUGGESTIONS_DATA_DIR
            / fpath.relative_to(dir_path).parent
            / f"suggestions-{fpath.name.rstrip(fpath.suffix)}.json",
            json.dumps(prefix_completions),
        )

        test_results = test_algorithm_completions(og_algorithm, prefix_completions)

        tested_fpath = (
            TESTED_DATA_DIR_PATH
            / fpath.relative_to(dir_path).parent
            / f"tested-{fpath.name.rstrip(fpath.suffix)}.csv"
        )

        tested_fpath.parent.mkdir(parents=True, exist_ok=True)
        test_results.to_csv(tested_fpath)
    pprint(
        f"Finished: {fpath.parent.name}/{fpath.name} : {datetime.now().strftime("%H:%M")}"
    )


def test_algorithm_completions(raw_algorithm: str, completions: dict) -> pd.DataFrame:
    df = pd.DataFrame(columns=const.SIMILARITY_ALGORITHMS.keys())
    for ratio, tabby_completed in completions.items():
        algorithms_test_results = {}
        for algorithm_name, algorithm in const.SIMILARITY_ALGORITHMS.items():
            result = algorithm(raw_algorithm, tabby_completed)
            algorithms_test_results[algorithm_name] = result

        df.loc[ratio] = algorithms_test_results

    return df


def generate_algorithm_splits_completions(
    raw_algorithm: str, split_ratios: list[float], session: requests.Session
):
    prefixes = process_data.generate_split_prefixes_by_percentage_ratios(
        raw_algorithm, split_ratios
    )

    algorithm_data = {}
    for ratio, prefix in zip(split_ratios, prefixes):
        while True:
            try:
                suggestion = session.get_suggestion(
                    "python",
                    prefix,
                )
            except requests.exceptions.HTTPError:
                time.sleep(30)
            else:
                first_tabby_suggestion = suggestion["choices"][0]["text"]
                tabby_completed_algorithm = prefix + first_tabby_suggestion
                algorithm_data[ratio] = tabby_completed_algorithm
                time.sleep(5)
                break

    return algorithm_data


if __name__ == "__main__":
    main()
