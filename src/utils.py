from pathlib import Path


def load_file(path: Path) -> str:
    with open(path, "r") as f:
        content = f.read()
        return content


def write_to_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
