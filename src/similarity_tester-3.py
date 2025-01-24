import os
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from difflib import SequenceMatcher
from collections.abc import Generator
from jellyfish import (
    damerau_levenshtein_distance,
    hamming_distance,
    jaro_winkler_similarity,
)
import utils
from prefix_generator import PrefixGenerator


class SimilarityTester:
    """Utility to test similarity of Tabby generated
    and original snippets using predefined algorithms.
    """

    def __init__(self, fragment_out_dir_path: Path, full_out_dir_path: Path):
        """
        Args:
            fragment_out_dir_path (Path): path to the directory
            to save similarity scores for overlap with generated fragments

            full_out_dir_path (Path): path to the directory
            to save similarity scores for full files
        """
        self._fragment_out_path = fragment_out_dir_path
        self._full_out_path = full_out_dir_path
        self.SIMILARITY_ALGORITHMS = {
            SequenceMatcher.__name__: lambda og, replica: SequenceMatcher(
                None, a=og, b=replica
            ).ratio(),
            damerau_levenshtein_distance.__name__: lambda og, replica: damerau_levenshtein_distance(
                og, replica
            ),
            hamming_distance.__name__: lambda og, replica: hamming_distance(
                og, replica
            ),
            jaro_winkler_similarity.__name__: lambda og, replica: jaro_winkler_similarity(
                og, replica
            ),
        }
        self._reset_dataframes()

    def _reset_dataframes(self):
        """clear contents of the dataframes, keeping the column indexes"""
        self._fragment_df = None
        self._full_df = None
        cols = list(self.SIMILARITY_ALGORITHMS.keys())
        self._fragment_df = pd.DataFrame(columns=cols)
        cols.append("original_duplicate_len_ratio")
        self._full_df = pd.DataFrame(columns=cols)

    def _total_file_count(self) -> int:
        """
        Returns:
            int: total number of files in input directory
        """
        sorted_dir = utils.get_data_dir() / "sorted"
        total = 0
        for root, dirs, files in os.walk(sorted_dir):
            total += len(files)
        return total

    def _next_reference_filepath(self) -> Generator[Path]:
        """
        Yields:
            Generator[Path]: paths to files in the input directory
        """
        sorted_dir = utils.get_data_dir() / "sorted"
        for fpath in sorted_dir.rglob("*"):
            if fpath.is_file():
                yield fpath

    def _next_completed_by_prefix(self, og_fpath: Path) -> Generator[tuple[int, Path]]:
        """
        Iterates through prefix-ratio directories in autocompleted directory,
        in each searching for the corresponding reference file path.
        Args:
            og_fpath (Path): reference file path

        Yields:
            Generator[tuple[int, Path]]: prefix_ratio of the prompt
            and path to file generated with this prompt
        """
        autocompletions_dir = utils.get_data_dir() / "autocompletions"
        og_relative_path = og_fpath.relative_to(utils.get_data_dir() / "sorted")
        for dir_ in autocompletions_dir.iterdir():
            prefix_ratio = dir_.name.split("-")[-1]
            for fpath in dir_.rglob("*"):
                if fpath.is_file():
                    relative_path = fpath.relative_to(dir_)
                    if relative_path == og_relative_path:
                        yield int(prefix_ratio), fpath

    def run(self):
        """Runs the similarity testing cycle for all files"""
        for og_fpath in tqdm(
            self._next_reference_filepath(),
            desc="Similarity testing",
            total=self._total_file_count(),
            leave=False,
        ):
            og_full = utils.load_file(og_fpath)
            for prefix_ratio, fpath in tqdm(
                self._next_completed_by_prefix(og_fpath),
                desc=f"{og_fpath.parent.name}/{og_fpath.name}",
                total=9,
                leave=False,
            ):
                replica_full = utils.load_file(fpath)

                split_idx = round(len(og_full) * prefix_ratio / 100)
                replica_part = replica_full[split_idx:]
                end_idx = min(
                    (split_idx + len(replica_part)),
                    (split_idx + len(og_full[split_idx:])),
                )
                og_part = og_full[split_idx:end_idx]

                self._run_similarity_algorithms_per_prefix_ratio(
                    og_full,
                    replica_full,
                    og_part,
                    replica_part,
                    prefix_ratio,
                    len(replica_full) / len(og_full),
                )
            self._save_results(og_fpath)
            self._reset_dataframes()

    def _run_similarity_algorithms_per_prefix_ratio(
        self,
        og_full: str,
        replica_full: str,
        og_part: str,
        replica_part: str,
        prefix_ratio: int,
        len_ratio: float,
    ):
        """
        Run similarity algorithms both for whole programs and for generated fragments only.
        Args:
            og_full (str): full content of reference program
            replica_full (str): full content of duplicate program per prefix ratio
            og_part (str): part of reference program overlapping with generated part
            replica_part (str): Tabby generated part
            prefix_ratio (int): ratio used to create prefix from reference program
            len_ratio (float): length ratio of Tabby-completed program to ther reference one
        """
        fragment_similarity_scores = {}
        full_similarity_scores = {}
        for algorithm_name, algorithm in self.SIMILARITY_ALGORITHMS.items():
            fragment_result = algorithm(og_part, replica_part)
            full_result = algorithm(og_full, replica_full)
            fragment_similarity_scores[algorithm_name] = fragment_result
            full_similarity_scores[algorithm_name] = full_result
        full_similarity_scores["original_duplicate_len_ratio"] = len_ratio
        self._fragment_df.loc[prefix_ratio] = fragment_similarity_scores
        self._full_df.loc[prefix_ratio] = full_similarity_scores

    def _save_results(self, og_fpath: Path):
        """
        Creates paths to save testing results, by recreating
         the relative structure of reference files from the source directory.
        Args:
            og_fpath (Path): reference file path
        """
        fragment_fpath = (
            self._fragment_out_path
            / og_fpath.relative_to(utils.get_data_dir() / "sorted").parent
            / f"{og_fpath.name.split('.')[0]}.csv"
        )
        full_fpath = (
            self._full_out_path
            / og_fpath.relative_to(utils.get_data_dir() / "sorted").parent
            / f"{og_fpath.name.split('.')[0]}.csv"
        )
        fragment_fpath.parent.mkdir(parents=True, exist_ok=True)
        full_fpath.parent.mkdir(parents=True, exist_ok=True)
        self._fragment_df.to_csv(fragment_fpath, float_format="%.4f")
        self._full_df.to_csv(full_fpath, float_format="%.4f")


def main():
    fragment_out_dir_path = utils.get_data_dir() / "similarity_logs_fragment"
    full_out_dir_path = utils.get_data_dir() / "similarity_logs_full"
    tester = SimilarityTester(fragment_out_dir_path, full_out_dir_path)
    tester.run()


if __name__ == "__main__":
    main()
