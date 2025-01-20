import time
import os
import click
from pathlib import Path
from dotenv import load_dotenv
from api_connection import TabbyConnection
from prefix_generator import PrefixGenerator
import const
import utils
import requests


class TabbySuggestionsFetcher:
    """
    Fetches suggestions from the Tabby server
    for each file's prefix increasing by ratio step,
    in the source directory
    """

    def __init__(
        self,
        tabby_connection: TabbyConnection,
        in_dir_path: Path,
        out_dir_path: Path,
        split_ratio_step: float,
        language: str,
        verbose: bool = True,
    ):
        self._tabby_connection = tabby_connection
        self._in_dir_path = in_dir_path
        self._out_dir_path = out_dir_path
        self._split_ratio_step = split_ratio_step
        self._language = language
        self._verbose = verbose

    def _next_filepath(self):
        for fpath in self._in_dir_path.rglob("*"):
            if fpath.is_file():
                yield fpath

    def run(self):
        """
        Main loop iterating over files
        and saving new version with completion
        for each prefix
        """
        for fpath in self._next_filepath():
            self._log_status(f"file: {fpath}")
            prefix_gen = PrefixGenerator(utils.load_file(fpath), self._split_ratio_step)
            for ratio, prefix, suffix in prefix_gen.next_prefix():
                self._log_status(f"ratio: {ratio:.2f}")

                response_data = self._await_request_response(prefix)
                first_suggestion = response_data["choices"][0]["text"]
                self._save_tabby_completed_code(fpath, ratio, prefix + first_suggestion)

    def _await_request_response(self, prefix: str):
        """
        Accommodates for possible timeouts of the server,
        given the potential intensity and frequency of the requests
        """
        while True:
            try:
                response_data = self._tabby_connection.get_suggestion(
                    self._language, prefix
                )
                return response_data
            except requests.HTTPError as e:
                self._log_status(f"request error: {e}")
                self._log_status(f"retrying in {const.REQUESTS_TIMEOUT} seconds")
                time.sleep(const.REQUESTS_TIMEOUT)

    def _save_tabby_completed_code(self, fpath: Path, ratio: float, content: str):
        """
        Saves Tabby completed prefix to a file,
        ordered in folders by prefix ratio
        """
        dest_fpath = (
            self._out_dir_path
            / f"prefix-ratio-{int(ratio * 100)}"
            / fpath.relative_to(self._in_dir_path)
        )
        utils.write_to_file(dest_fpath, content)
        self._log_status(f"saved: {dest_fpath}")

    def _log_status(self, message):
        """Prints message to stdout if verbose mode is enabled"""
        if self._verbose:
            print(message)


@click.command()
@click.option(
    "--in-dir-path",
    required=True,
    help="path to a directory which contents will be sent to Tabby for suggestions",
)
@click.option(
    "--out-dir-path",
    required=True,
    help="path to a directory suggestions from Tabby will be saved",
)
@click.option(
    "--split-ratio-step",
    required=True,
    type=click.FLOAT,
    help="Float value (0,1) for the file split step ratio",
)
@click.option(
    "--language",
    required=True,
    help="programming language of the prefix",
    default="python",
)
@click.option("--verbose", help="verbose mode", is_flag=True)
def main(
    in_dir_path: str,
    out_dir_path: str,
    split_ratio_step: float,
    language: str,
    verbose: bool,
):
    load_dotenv()
    tabby_auth_token = os.environ["tabby_auth_token"]

    try:
        in_dir_path = Path(in_dir_path).resolve(strict=True)
        out_dir_path = Path(out_dir_path).resolve(strict=True)
    except OSError as e:
        print(e)
    else:
        fetcher = TabbySuggestionsFetcher(
            TabbyConnection(const.TABBY_URL, tabby_auth_token),
            Path(in_dir_path).resolve(strict=True),
            Path(out_dir_path).resolve(strict=True),
            float(split_ratio_step),
            language,
            bool(verbose),
        )
        fetcher.run()


if __name__ == "__main__":
    main()
