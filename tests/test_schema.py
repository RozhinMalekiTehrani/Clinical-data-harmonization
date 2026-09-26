import json

from src.validation import (
    validate_record
)


def test_schema_validation():

    record = {
        "schema_version": "1.0",
        "patient": {
            "source_patient_id": "P1007",
            "birth_date": None
        },
        "encounter": {
            "source_encounter_id": None,
            "event_time": None
        },
        "facts": [],
        "quality": {
            "missing": [],
            "unknown": [],
            "not_mentioned": [],
            "conflicting": [],
            "missing_required": [],
            "conflicts": [],
            "warnings": []
        }
    }

    schema_path = (
        "schemas/canonical_record.json"
    )

    assert validate_record(
        record,
        schema_path
    )