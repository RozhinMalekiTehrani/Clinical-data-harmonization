from datetime import datetime

from .mappings import (
    map_lab_code,
    normalize_unit,
    normalize_numeric_value
)


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).isoformat()

    except ValueError:
        return None


def process_csv_record(
    record,
    row_index,
    document_id,
    mapping
):
    patient_id = record.get("patient_id") or None
    local_code = record.get("test_code") or None
    test_name = record.get("test_name") or None
    raw_value = record.get("result_value") or None
    raw_unit = record.get("result_unit") or None
    raw_time = record.get("result_time") or None

    missing = []
    warnings = []

    concept = map_lab_code(
        local_code,
        mapping
    )

    if concept is None:
        missing.append("unknown_local_code")

    if raw_unit is None:
        missing.append("missing_unit")

    normalized_time = parse_datetime(
        raw_time
    )

    if raw_time and normalized_time is None:
        missing.append("invalid_date")

    unit_config = normalize_unit(
        test_name,
        raw_unit,
        mapping
    )

    normalized_value = normalize_numeric_value(
        raw_value,
        unit_config
    ) if unit_config else None

    if raw_value is not None and normalized_value is None:
        missing.append("invalid_numeric_value")

    if not patient_id:
        missing.append("missing_patient_id")

    if concept is None:
        concept = {
            "system": "LOCAL",
            "code": local_code,
            "display": test_name
        }

    if missing:
        review_status = "needs_review"
    else:
        review_status = "accepted"

    canonical_unit = (
        unit_config["canonical_unit"]
        if unit_config
        else raw_unit
    )

    fact = {
        "category": "observation",
        "concept": concept,
        "value": {
            "number": normalized_value,
            "text": None,
            "unit": canonical_unit
        },
        "assertion": "present",
        "temporality": "current",
        "effective_time": normalized_time,
        "source_ref": {
            "document_id": document_id,
            "field_path": (
                f"row[{row_index}].result_value"
            ),
            "text_span": None
        },
        "extraction_method": "dictionary",
        "review_status": review_status
    }

    return {
        "schema_version": "1.0",
        "patient": {
            "source_patient_id": patient_id,
            "birth_date": None
        },
        "encounter": {
            "source_encounter_id": None,
            "event_time": normalized_time
        },
        "facts": [fact],
        "quality": {
            "missing": [],
            "unknown": (
                ["local_code"]
                if "unknown_local_code" in missing
                else []
            ),
            "not_mentioned": [],
            "conflicting": [],
            "missing_required": missing,
            "conflicts": [],
            "warnings": warnings
        }
    }