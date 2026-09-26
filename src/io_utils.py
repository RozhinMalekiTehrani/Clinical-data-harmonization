from pathlib import Path
import csv
import json


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_csv_records(filename: str):
    path = PROJECT_ROOT / "data" / "structured" / filename

    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_narrative(filename: str):
    path = PROJECT_ROOT / "data" / "unstructured" / filename

    with path.open("r", encoding="utf-8") as f:
        return f.read()


def load_mapping(filename: str):
    path = PROJECT_ROOT / "config" / filename

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)