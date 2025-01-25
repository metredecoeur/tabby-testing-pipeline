import os
import subprocess
import io
import re

from collections.abc import Generator
from typing import Union
from tqdm import tqdm
from pathlib import Path
import pandas as pd

from utils import get_data_dir
import const


class StaticTester:
    """Utility to test Tabby generated code using static evaluation metrics:
    - cyclomatic complexity
    - halstead effort
    - halstead bugs
    """

    def __init__(self, out_dir_path: Path):
        """
        Args:
            out_dir_path (Path): path to save the testing scores
        """
        self._out_dir_path = out_dir_path
        self._complexity_command = [
            "radon",
            "cc",
            "--total-average",
            "-s",
        ]
        self._halstead_command = [
            "radon",
            "hal",
        ]
        self._reset_dataframe()

    def _reset_dataframe(self):
        """
        Clears the dataframe, keeping the column indexes
        """
        self._results_df = None
        cols = const.METRICS
        self._results_df = pd.DataFrame(columns=cols)

    def _next_reference_filepath(self):
        """
        Yields:
            Generator[Path]: paths to files in the input directory
        """
        sorted_dir = get_data_dir() / "sorted"
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
        autocompletions_dir = get_data_dir() / "autocompletions"
        og_relative_path = og_fpath.relative_to(get_data_dir() / "sorted")
        for dir_ in autocompletions_dir.iterdir():
            prefix_ratio = dir_.name.split("-")[-1]
            for fpath in dir_.rglob("*"):
                if fpath.is_file():
                    relative_path = fpath.relative_to(dir_)
                    if relative_path == og_relative_path:
                        yield int(prefix_ratio), fpath

    def _get_cc_complexity(self, cc_output: str) -> Union[float, None]:
        """Get complexity value from Radon's output

        Args:
            cc_output (str): Radon's command output for cyclomatic complexity

        Returns:
            Union[float, None]: complexity value,
            or None if no matches found
        """
        pattern = r"Average complexity:\s*(\w) \(([\d.]+)\)"
        match = re.search(pattern, cc_output)
        if match:
            return float(match.group(2))
        else:
            return None

    def _get_halstead_effort_bugs(
        self, halstead_output: str
    ) -> Union[tuple[float, float], None]:
        """Get Halsted bugs and effort values from Radon's output

        Args:
            halstead_output (str): Radon's command output for Halstead metrics

        Returns:
            Union[tuple[float, float], None]: tuple of (effort, bugs),
            or None if no matches found
        """
        pattern = r"effort:\s*([\d.]+).*?bugs:\s*([\d.]+)"
        match = re.search(pattern, halstead_output, re.DOTALL)

        if match:
            effort = float(match.group(1))
            bugs = float(match.group(2))
            return effort, bugs
        else:
            return None, None

    def _total_file_count(self) -> int:
        """
        Returns:
            int: total number of files in input directory
        """
        sorted_dir = get_data_dir() / "sorted"
        total = 0
        for root, dirs, files in os.walk(sorted_dir):
            total += len(files)
        return total

    def run(self):
        """Run static evaluation testing cycle on all files"""
        for fpath in tqdm(
            self._next_reference_filepath(),
            desc="Static evaluation",
            total=self._total_file_count(),
            leave=False,
        ):
            og_cc_complexity, og_hal_effort, og_hal_bugs = self._run_subprocesses(fpath)
            self._results_df.loc["original"] = [
                og_cc_complexity,
                og_hal_effort,
                og_hal_bugs,
            ]
            for prefix_ratio, completion_path in tqdm(
                self._next_completed_by_prefix(fpath),
                desc=f"{fpath.parent.name}/{fpath.name}",
                total=9,
                leave=False,
            ):
                cc_complexity, hal_effort, hal_bugs = self._run_subprocesses(
                    completion_path
                )
                self._results_df.loc[str(prefix_ratio)] = [
                    cc_complexity,
                    hal_effort,
                    hal_bugs,
                ]
            self._save_results(fpath)
            self._reset_dataframe()

    def _save_results(self, og_fpath: Path):
        """
        Creates path to save testing results, by recreating
         the relative structure of reference file from the source directory.
        Args:
            og_fpath (Path): reference file path
        """
        dest_fpath = (
            self._out_dir_path
            / og_fpath.relative_to(get_data_dir() / "sorted").parent
            / f"{og_fpath.name.split('.')[0]}.csv"
        )
        dest_fpath.parent.mkdir(parents=True, exist_ok=True)
        self._results_df.to_csv(dest_fpath, float_format="%.4f")

    def _run_subprocesses(self, fpath: Path) -> Union[tuple[float, float, float], None]:
        """

        Args:
            fpath (Path): path for which to run the evaluation

        Returns:
            Union[tuple[float, float, float], None]: Metric score values,
            extracted from Radon's commands outputs
        """
        hal_effort, hal_bugs, cc_complexity = 0, 0, 0

        cc_process = subprocess.run(
            args=[*self._complexity_command, fpath], capture_output=True, text=True
        )
        if cc_process.returncode == 0:
            cc_output = cc_process.stdout
            cc_complexity = self._get_cc_complexity(cc_output)
            if cc_complexity is None:
                cc_complexity = 0
        else:
            cc_complexity = 0

        hal_process = subprocess.run(
            args=[*self._halstead_command, fpath], capture_output=True, text=True
        )
        if hal_process.returncode == 0:
            hal_output = hal_process.stdout
            hal_effort, hal_bugs = self._get_halstead_effort_bugs(hal_output)
            if hal_effort is None:
                hal_effort = 0
            if hal_bugs is None:
                hal_bugs = 0
        else:
            hal_effort, hal_bugs = 0, 0

        return cc_complexity, hal_effort, hal_bugs


def main():
    out_dir_path = get_data_dir() / "static_metrics"
    tester = StaticTester(out_dir_path)
    tester.run()


if __name__ == "__main__":
    main()
