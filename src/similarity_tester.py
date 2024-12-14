import click
import const
import pandas as pd
from pathlib import Path
from difflib import SequenceMatcher
from jellyfish import (
    damerau_levenshtein_distance,
    hamming_distance,
    jaro_winkler_similarity,
)
import utils


class SimilarityTest:
    def __init__(self, out_dir_path: Path, verbose: bool = True):
        self._out_dir_path = out_dir_path
        self._verbose = verbose
        self.SIMILARITY_ALGORITHMS = {
            SequenceMatcher.__name__: lambda og, replica: SequenceMatcher(
                isjunk=None, a=og, b=replica
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

        self._current_dataframe = pd.DataFrame(
            columns=self.SIMILARITY_ALGORITHMS.keys()
        )

    def _clear_dataframe(self):
        self._current_dataframe.drop(self._current_dataframe.index, inplace=True)

    def _next_reference_filepath(self) -> Path:
        for fpath in const.PRE_SORTED_DATA_DIR.rglob("*"):
            if fpath.is_file():
                yield fpath

    def _next_completed_by_prefix(self, og_fpath: Path) -> tuple[str, Path]:
        for dir in const.TABBY_SUGGESTIONS_DATA_DIR.iterdir():
            prefix_ratio = dir.name.split("-")[-1]
            for fpath in dir.rglob("*"):
                if fpath.is_file() and fpath.name == og_fpath.name:
                    yield prefix_ratio, fpath

    def run(self):
        for og_fpath in self._next_reference_filepath():
            for prefix_ratio, fpath in self._next_completed_by_prefix(og_fpath):
                self._run_similarity_algorithms_per_prefix_ratio(
                    og_fpath, fpath, prefix_ratio
                )
            self._save_results(og_fpath)
            self._clear_dataframe()

    def _run_similarity_algorithms_per_prefix_ratio(
        self, og_fpath: Path, fpath: Path, prefix_ratio: str
    ):
        algorithms_test_results = {}
        for algorithm_name, algorithm in self.SIMILARITY_ALGORITHMS.items():
            result = algorithm(utils.load_file(og_fpath), utils.load_file(fpath))
            algorithms_test_results[algorithm_name] = result

        self._current_dataframe.loc[prefix_ratio] = algorithms_test_results

    def _save_results(self, og_fpath: Path):
        dest_fpath = (
            self._out_dir_path
            / og_fpath.relative_to(const.PRE_SORTED_DATA_DIR).parent
            / f"{og_fpath.name}.csv"
        )
        dest_fpath.parent.mkdir(parents=True, exist_ok=True)
        self._current_dataframe.to_csv(dest_fpath)
        self._log_status(f"tested and saved: {dest_fpath}")

    def _log_status(self, message):
        """Prints message to stdout if verbose mode is enabled"""
        if self._verbose:
            print(message)


@click.command()
@click.option(
    "--out-dir-path",
    required=True,
    help="path to a directory suggestions from Tabby will be saved",
)
@click.option("--verbose", help="verbose mode", is_flag=True)
def main(
    out_dir_path: str,
    verbose: bool,
):
    try:
        out_dir_path = Path(out_dir_path).resolve(strict=True)
    except OSError as e:
        print(e)
    else:
        tester = SimilarityTest(out_dir_path)
        tester.run()


if __name__ == "__main__":
    main()
