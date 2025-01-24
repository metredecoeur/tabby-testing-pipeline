import time
import os
from tqdm import tqdm
import requests
from pathlib import Path
from dotenv import load_dotenv
from collections.abc import Generator

import const
import utils
from tabby_connection import TabbyConnection
from prefix_generator import PrefixGenerator


class TabbySuggestionsFetcher:
    """
    Fetches suggestions from the Tabby server
    for increasingly longer prefixes selected
    from reference program files using split_ratio_step
    and saves the autocompleted files to a new location
    """

    def __init__(
        self,
        tabby_connection: TabbyConnection,
        in_dir_path: Path,
        out_dir_path: Path,
        split_ratio_step: float,
        language: str,
    ):
        """
        Args:
            tabby_connection (TabbyConnection): api connection utility
            in_dir_path (Path): sorted database
            out_dir_path (Path): _description_
            split_ratio_step (float): _description_
            language (str): _description_
            verbose (bool, optional): _description_. Defaults to True.
        """
        self._tabby_connection = tabby_connection
        self._in_dir_path = in_dir_path
        self._out_dir_path = out_dir_path
        self._split_ratio_step = split_ratio_step
        self._language = language

    def _total_file_count(self) -> int:
        """
        Returns:
            int: total number of files in input directory
        """
        total = 0
        for root, dirs, files in os.walk(self._in_dir_path):
            total += len(files)
        return total

    def _next_filepath(self) -> Generator[Path]:
        """
        Yields:
            Generator[Path]: next path from input directory
        """
        for fpath in self._in_dir_path.rglob("*"):
            if fpath.is_file():
                yield fpath

    def run(self):
        """
        Main loop iterating over files
        and saving new version with completion
        for each prefix
        """
        start = time.perf_counter()
        for fpath in tqdm(
            self._next_filepath(),
            desc="Fetching autocompletions",
            total=self._total_file_count(),
            leave=False,
        ):
            og_content = utils.load_file(fpath)
            prefix_gen = PrefixGenerator(utils.load_file(fpath), self._split_ratio_step)
            for ratio, prefix, _ in tqdm(
                prefix_gen.next_prefix(),
                desc=f"{fpath.parent.name}/{fpath.name}",
                total=9,
                leave=False,
            ):
                first_suggestion = ""
                response_data = self._await_request_response(prefix)
                first_suggestion = response_data["choices"][0]["text"]
                prefix += first_suggestion
                self._save_tabby_completed_code(fpath, ratio, prefix)

        end = time.perf_counter()
        benchmark_msg = "Total time: {:.sf}s".format(end - start)
        tqdm.write("Fetching autocompletions done!")
        tqdm.write(benchmark_msg)
        utils.write_to_file(
            utils.get_data_dir() / "requests_timing.json", benchmark_msg
        )

    def _await_request_response(self, prefix: str):
        """Accommodates for possible timeouts of the server,
        given the potential intensity and frequency of the requests

        Args:
            prefix (str): prefix to be used for the request
        """
        while True:
            try:
                response_data = self._tabby_connection.get_suggestion(
                    self._language, prefix
                )
                return response_data
            except requests.HTTPError as e:
                time.sleep(const.REQUESTS_TIMEOUT)

    def _save_tabby_completed_code(self, fpath: Path, ratio: float, content: str):
        """Saves Tabby completed prefix to a file,
        ordered in folders by prefix ratio

        Args:
            fpath (Path): path of currently processed reference file
            ratio (float): ratio of the current split
            content (str): prefix generated with ratio, autocompleted by Tabby
        """
        dest_fpath = (
            self._out_dir_path
            / f"prefix-ratio-{int(ratio * 100)}"
            / fpath.relative_to(self._in_dir_path)
        )
        utils.write_to_file(dest_fpath, content)


def main():
    load_dotenv()
    tabby_auth_token = os.getenv("tabby_auth_token")
    sorted_db_path = utils.get_data_dir() / "sorted"
    out_dir_path = utils.get_data_dir() / "autocompletions"
    fetcher = TabbySuggestionsFetcher(
        TabbyConnection(const.TABBY_URL, tabby_auth_token),
        sorted_db_path,
        out_dir_path,
        const.SPLIT_RATIO_STEP,
        const.DEFAULT_LANGUAGE,
    )
    fetcher.run()


if __name__ == "__main__":
    main()
