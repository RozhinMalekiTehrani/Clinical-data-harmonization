from datetime import datetime
from .mappings import map_local_lab_code, normalize_unit


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
    except ValueError:
        return None


def process_csv_record(record, row_idx, document_id, mapping):
    patient_id = record.get("patient_id") or None
    local_code = record.get("test_code") or None
    test_name = record.get("test_name") or None
    raw_value = record.get("result_value") or None
    raw_unit = record.get("result_unit") or None
    raw_time = record.get("result_time") or None

    concept = map_local_lab_code(local_code, mapping)

    missing_required = []
    warnings = []

    if not patient_id:
        missing_required.append("patient_id")

    if not raw_value:
        missing_required.append("result_value")

    if not raw_unit:
        missing_required.append("result_unit")

    parsed_time = parse_datetime(raw_time)

    if raw_time and parsed_time is None:
        missing_required.append("invalid_result_time")

    if concept is None:
        missing_required.append("unmapped_local_code")

    numeric_value = None

    if raw_value:
        try:
            numeric_value = float(raw_value)
        except ValueError:
            warnings.append("result_value_not_numeric")

    canonical_unit = None

    if concept and raw_unit:
        canonical_unit = normalize_unit(
            concept["display"],
            raw_unit,
            mapping
        )

        if canonical_unit is None:
            missing_required.append("unresolved_unit")

    review_status = (
        "needs_review"
        if missing_required
        else "accepted"
    )

    fact = {
        "category": "observation",
        "concept": concept or {
            "system": "LOCAL_UNMAPPED",
            "code": local_code,
            "display": test_name
        },
        "value": {
            "number": numeric_value,
            "text": None,
            "unit": canonical_unit
        },
        "assertion": "present",
        "temporality": "current",
        "effective_time": parsed_time,
        "source_ref": {
            "document_id": document_id,
            "field_path": f"row[{row_idx}].result_value",
            "text_span": None
        },
        "extraction_method": "dictionary",
        "review_status": review_status
    }

    return {
        "schema_version": "1.0",
        "patient": {
            "source_patient_id": patient_id,
            "birth_date": record.get("birth_date") or None
        },
        "encounter": {
            "source_encounter_id": record.get("encounter_id") or None,
            "event_time": parsed_time
        },
        "facts": [fact],
        "quality": {
            "missing_required": missing_required,
            "conflicts": [],
            "warnings": warnings
        }
    }