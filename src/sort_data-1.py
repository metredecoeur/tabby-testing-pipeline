import click
import shutil
import argparse


from pathlib import Path


class DataSorter:
    def __init__(
        self, in_dir_path: Path, out_dir_path: Path, file_extensions: list[str]
    ):
        self._in_dir_path = in_dir_path
        self._out_dir_path = out_dir_path
        self._file_extensions = file_extensions

    def _file_extension_allowed(self, fpath: Path) -> bool:
        file_extension_without_dot = fpath.suffix[1:]
        return any([file_extension_without_dot == ext for ext in self._file_extensions])

    def _file_not_empty(self, fpath: Path) -> bool:
        return fpath.stat().st_size != 0

    def _next_matching_filepath(self) -> Path:
        for f in self._in_dir_path.rglob("*"):
            if (
                f.is_file()
                and self._file_extension_allowed(f)
                and self._file_not_empty(f)
            ):
                yield f

    def _copy_file_from_to(self, source: Path, destination: Path):
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination, follow_symlinks=False)

    def run(self):
        for fpath in self._next_matching_filepath():
            self._copy_file_from_to(
                fpath, self._out_dir_path / fpath.relative_to(self._in_dir_path.parent)
            )


@click.command()
@click.option(
    "--in-dir-path",
    required=True,
    help="path to a directory which contents will be sorted to leave only source code files",
)
@click.option(
    "--out-dir-path",
    required=True,
    help="path to a directory where sorted in_dir structure will be saved",
)
@click.option(
    "--file-extension",
    required=True,
    multiple=True,
    help="Extensions of the files to be kept in the sorted codebase passed without leading dots",
)
def main(in_dir_path: str, out_dir_path: str, file_extension: list[str]):
    sorter = DataSorter(Path(in_dir_path), Path(out_dir_path), file_extension)
    sorter.run()


if __name__ == "__main__":
    main()
