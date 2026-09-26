from pathlib import Path
import csv
import json


# --------------------------------------------------
# Project paths
# --------------------------------------------------

# The project root is the parent directory of src/
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = PROJECT_ROOT / "config"
OUTPUT_DIR = PROJECT_ROOT / "outputs"


# --------------------------------------------------
# Data loading
# --------------------------------------------------

def load_csv_records(filename: str):
    """Load a structured CSV file from data/structured/."""

    csv_path = DATA_DIR / "structured" / filename

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_narrative(filename: str):
    """Load a narrative text file from data/unstructured/."""

    txt_path = DATA_DIR / "unstructured" / filename

    with txt_path.open("r", encoding="utf-8") as f:
        return f.read()


def load_mapping(filename: str):
    """Load an organization-specific mapping configuration."""

    config_path = CONFIG_DIR / filename

    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------
# Test loading
# --------------------------------------------------

if __name__ == "__main__":

    csv_records = load_csv_records("patient_lab_results.csv")
    narrative_text = load_narrative("note_N204.txt")
    local_mapping = load_mapping("hospital_a_mappings.json")

    print("CSV loaded:")
    print(csv_records)

    print("\nNarrative loaded:")
    print(narrative_text)

    print("\nMapping loaded:")
    print(local_mapping)