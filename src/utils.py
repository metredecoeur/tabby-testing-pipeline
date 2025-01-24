from pathlib import Path

project_dir = Path(__file__).resolve().parents[1]


def get_data_dir() -> Path:
    return project_dir / "data"


def get_plots_dir() -> Path:
    return project_dir / "plots"


def load_file(path: Path) -> str:
    with open(path, "r") as f:
        content = f.read()
        return content


def write_to_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
