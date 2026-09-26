from pathlib import Path
import csv
import json


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_csv_records(filename):
    path = PROJECT_ROOT / "data" / "structured" / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Structured input not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as file:
        return list(csv.DictReader(file))


def load_narrative(filename):
    path = PROJECT_ROOT / "data" / "unstructured" / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Narrative input not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


def load_json(filename, directory):
    path = PROJECT_ROOT / directory / filename

    if not path.exists():
        raise FileNotFoundError(
            f"JSON file not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def save_json(data, filename):
    output_dir = PROJECT_ROOT / "outputs"

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = output_dir / filename

    with output_path.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            sort_keys=True,
            ensure_ascii=False
        )

    return output_path