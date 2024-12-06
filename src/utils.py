

def load_file(path: str) -> str:
    with open(path, "r") as f:
        content = f.read()
        return content


def save_file(path: str, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
