import shutil
import argparse


from pathlib import Path
from typing import List

CWD = Path(__file__).parent


def file_is_of_extension(file_path: Path, extensions: List[str]) -> bool:
    file_extension_without_dot = file_path.suffix[1:]
    return any([file_extension_without_dot == ext for ext in extensions])


def file_contents_empty(file_obj: Path) -> bool:
    return file_obj.stat().st_size == 0


def copy_file_from_to(source: Path, destination: Path):
    # make sure the parent exists
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination, follow_symlinks=False)


def sort_initial_database(data_dir_path: Path, allowed_extensions: List[str]):
    all_files = [
        f
        for f in data_dir_path.rglob("*")
        if f.is_file()
        and (not file_contents_empty(f))
        and file_is_of_extension(f, allowed_extensions)
    ]
    sorted_data_dir_name = f"sorted-{data_dir_path.name}"
    # get relative path from cwd
    for file_obj in all_files:
        sorted_dest_filepath = (
            CWD / sorted_data_dir_name / file_obj.relative_to(data_dir_path)
        )
        # recreate relative path in sorted_data_dir
        copy_file_from_to(file_obj, sorted_dest_filepath)


def main():
    parser = argparse.ArgumentParser(
        prog="Data Sorter",
        description="Programme for sorting raw codebase for further testing",
    )

    parser.add_argument(
        "raw_db_path",
        help=f"Path to the raw database to be sorted, relative to {__file__}",
    )

    parser.add_argument(
        "file_extensions",
        help="Extensions of the files to be kept in the sorted codebase passed without leading dots",
        action="extend",
        nargs="+",
    )

    args = parser.parse_args()
    
    data_path = Path(args.raw_db_path)  # it may be relative

    sort_initial_database(data_path, args.file_extensions)


if __name__ == "__main__":
    main()
