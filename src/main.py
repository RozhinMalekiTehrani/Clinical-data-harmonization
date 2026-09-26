import argparse
import json
from pathlib import Path

from .io_utils import (
    load_csv_records,
    load_narrative,
    load_mapping
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--structured",
        required=True
    )

    parser.add_argument(
        "--narrative",
        required=True
    )

    parser.add_argument(
        "--mapping",
        required=True
    )

    args = parser.parse_args()

    mapping = load_mapping(args.mapping)

    csv_records = load_csv_records(
        args.structured
    )

    narrative_text = load_narrative(
        args.narrative
    )

    print(
        f"Loaded {len(csv_records)} structured records."
    )

    print(
        f"Loaded narrative document "
        f"with {len(narrative_text)} characters."
    )

    print(
        f"Loaded mapping version: "
        f"{mapping.get('mapping_version')}"
    )


if __name__ == "__main__":
    main()