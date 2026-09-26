import argparse
from pathlib import Path

from .io_utils import (
    PROJECT_ROOT,
    load_csv_records,
    load_narrative,
    load_json,
    save_json
)

from .narrative import load_nlp

from .pipeline import run_pipeline


DEFAULT_STRUCTURED = (
    "patient_lab_results.csv"
)

DEFAULT_NARRATIVE = (
    "note_N204.txt"
)

DEFAULT_MAPPING = (
    "hospital_a_mappings.json"
)


def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Clinical data harmonization "
            "prototype"
        )
    )

    parser.add_argument(
        "--structured",
        default=DEFAULT_STRUCTURED,
        help=(
            "CSV filename inside "
            "data/structured/"
        )
    )

    parser.add_argument(
        "--narrative",
        default=DEFAULT_NARRATIVE,
        help=(
            "Narrative filename inside "
            "data/unstructured/"
        )
    )

    parser.add_argument(
        "--mapping",
        default=DEFAULT_MAPPING,
        help=(
            "Mapping filename inside "
            "config/"
        )
    )

    return parser.parse_args()


def main():

    args = parse_args()

    print(
        "Starting clinical data "
        "harmonization..."
    )

    structured_records = load_csv_records(
        args.structured
    )

    narrative_text = load_narrative(
        args.narrative
    )

    mapping = load_json(
        args.mapping,
        "config"
    )

    schema_path = (
        PROJECT_ROOT
        / "schemas"
        / "canonical_record.json"
    )

    print(
        f"Structured records loaded: "
        f"{len(structured_records)}"
    )

    print(
        f"Narrative characters loaded: "
        f"{len(narrative_text)}"
    )

    print(
        f"Organization: "
        f"{mapping['organization_id']}"
    )

    print(
        f"Mapping version: "
        f"{mapping['mapping_version']}"
    )

    print(
        "Loading biomedical NLP model..."
    )

    nlp = load_nlp()

    result = run_pipeline(
        structured_records=structured_records,
        narrative_text=narrative_text,
        mapping=mapping,
        structured_document_id=args.structured,
        narrative_document_id=args.narrative,
        schema_path=schema_path,
        nlp=nlp
    )

    canonical_path = save_json(
        result["canonical_record"],
        "canonical_record.json"
    )

    review_path = save_json(
        result["review_queue"],
        "review_queue.json"
    )

    print()
    print(
        "Pipeline completed successfully."
    )

    print(
        f"Canonical output: "
        f"{canonical_path}"
    )

    print(
        f"Review queue: "
        f"{review_path}"
    )

    print(
        f"Facts produced: "
        f"{len(result['canonical_record']['facts'])}"
    )

    print(
        f"Review items: "
        f"{len(result['review_queue'])}"
    )


if __name__ == "__main__":
    main()