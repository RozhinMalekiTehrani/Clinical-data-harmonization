import json
from pathlib import Path

import spacy

from src.io_utils import (
    load_csv_records,
    load_narrative,
    load_json
)

from src.pipeline import run_pipeline


def test_replay_is_deterministic(tmp_path):

    root = Path(__file__).resolve().parents[1]

    structured = load_csv_records(
        "patient_lab_results.csv"
    )

    narrative = load_narrative(
        "note_N204.txt"
    )

    mapping = load_json(
        "hospital_a_mappings.json",
        "config"
    )

    schema_path = (
        root
        / "schemas"
        / "canonical_record.json"
    )

    nlp = spacy.load(
        "en_core_sci_sm"
    )

    first = run_pipeline(
        structured_records=structured,
        narrative_text=narrative,
        mapping=mapping,
        structured_document_id=(
            "patient_lab_results.csv"
        ),
        narrative_document_id=(
            "note_N204.txt"
        ),
        schema_path=schema_path,
        nlp=nlp
    )

    second = run_pipeline(
        structured_records=structured,
        narrative_text=narrative,
        mapping=mapping,
        structured_document_id=(
            "patient_lab_results.csv"
        ),
        narrative_document_id=(
            "note_N204.txt"
        ),
        schema_path=schema_path,
        nlp=nlp
    )

    first_bytes = json.dumps(
        first,
        indent=2,
        sort_keys=True
    ).encode("utf-8")

    second_bytes = json.dumps(
        second,
        indent=2,
        sort_keys=True
    ).encode("utf-8")

    assert first_bytes == second_bytes