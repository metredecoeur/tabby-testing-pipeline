import shutil
import argparse

from pathlib import Path
from collections.abc import Generator

from utils import get_data_dir


class DataSorter:
    """
    Utility for sorting raw dataset,
    by keeping only the files with allowed extensions
    and removing the ones that are empty
    """

    def __init__(
        self, in_dir_path: Path, out_dir_path: Path, file_extensions: list[str]
    ):
        """
        Args:
            in_dir_path (Path): path to raw/unsorted dataset
            out_dir_path (Path): destination path to save sorted copy of raw dataset
            file_extensions (list[str]): allowed extensions of the files to keep
        """
        self._in_dir_path = in_dir_path
        self._out_dir_path = out_dir_path
        self._file_extensions = file_extensions

    def _file_extension_allowed(self, fpath: Path) -> bool:
        """Check if extension of file is on allowed list

        Args:
            fpath (Path): filepath to check

        Returns:
            bool: True for allowed extension, False otherwise
        """
        file_extension_without_dot = fpath.suffix[1:]
        return any([file_extension_without_dot == ext for ext in self._file_extensions])

    def _file_not_empty(self, fpath: Path) -> bool:
        """Checks if file's contents are not empty

        Args:
            fpath (Path): filepath to check

        Returns:
            bool: True for file not empty, False otherwise
        """
        return fpath.stat().st_size != 0

    def _next_matching_filepath(self) -> Generator[Path]:
        """Iterates over and yields files from the raw dataset
         that fit the sorting criteria

        Yields:
            Generator[Path]: matching filepath
        """
        for f in self._in_dir_path.rglob("*"):
            if (
                f.is_file()
                and self._file_extension_allowed(f)
                and self._file_not_empty(f)
            ):
                yield f

    def _copy_file_from_to(self, source: Path, destination: Path):
        """Copy file from source to destination

        Args:
            source (Path): file's original location
            destination (Path): destination for file's copy
        """
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination, follow_symlinks=False)

    def run(self):
        """Perform sorting by copying for the whole raw database"""
        for fpath in self._next_matching_filepath():
            self._copy_file_from_to(
                fpath, self._out_dir_path / fpath.relative_to(self._in_dir_path)
            )


def main():
    raw_db_path: Path = get_data_dir() / "raw"
    sorted_db_path: Path = get_data_dir() / "sorted"
    sorter = DataSorter(raw_db_path, sorted_db_path, ["py"])
    sorter.run()


if __name__ == "__main__":
    main()
