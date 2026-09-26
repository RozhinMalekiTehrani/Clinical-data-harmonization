from src.structured import process_csv_record


MAPPING = {
    "lab_codes": {
        "LAB-44": {
            "system": "LOINC",
            "code": "718-7",
            "display": "Hemoglobin"
        }
    },
    "unit_conversions": {
        "Hb": {
            "g/dL": {
                "canonical_unit": "g/dL",
                "factor": 1.0,
                "offset": 0.0
            }
        }
    }
}


def test_valid_structured_record():

    record = {
        "patient_id": "P1007",
        "test_code": "LAB-44",
        "test_name": "Hb",
        "result_value": "12.1",
        "result_unit": "g/dL",
        "result_time": (
            "2026-08-11T09:30:00Z"
        )
    }

    result = process_csv_record(
        record,
        0,
        "patient_lab_results.csv",
        MAPPING
    )

    fact = result["facts"][0]

    assert (
        result["patient"]["source_patient_id"]
        == "P1007"
    )

    assert fact["value"]["number"] == 12.1

    assert fact["value"]["unit"] == "g/dL"

    assert (
        fact["review_status"]
        == "accepted"
    )

    assert (
        fact["source_ref"]["field_path"]
        == "row[0].result_value"
    )


def test_missing_unit_requires_review():

    record = {
        "patient_id": "P1007",
        "test_code": "LAB-44",
        "test_name": "Hb",
        "result_value": "12.1",
        "result_unit": "",
        "result_time": (
            "2026-08-11T09:30:00Z"
        )
    }

    result = process_csv_record(
        record,
        0,
        "missing_unit.csv",
        MAPPING
    )

    assert "missing_unit" in (
        result["quality"]["missing_required"]
    )

    assert (
        result["facts"][0]["review_status"]
        == "needs_review"
    )


def test_unknown_local_code_requires_review():

    record = {
        "patient_id": "P1007",
        "test_code": "UNKNOWN-999",
        "test_name": "Hb",
        "result_value": "12.1",
        "result_unit": "g/dL",
        "result_time": (
            "2026-08-11T09:30:00Z"
        )
    }

    result = process_csv_record(
        record,
        0,
        "unknown_code.csv",
        MAPPING
    )

    assert "unknown_local_code" in (
        result["quality"]["missing_required"]
    )

    assert (
        result["facts"][0]["review_status"]
        == "needs_review"
    )


def test_corrupted_date_requires_review():

    record = {
        "patient_id": "P1007",
        "test_code": "LAB-44",
        "test_name": "Hb",
        "result_value": "12.1",
        "result_unit": "g/dL",
        "result_time": "2026-99-99"
    }

    result = process_csv_record(
        record,
        0,
        "bad_date.csv",
        MAPPING
    )

    assert "invalid_date" in (
        result["quality"]["missing_required"]
    )

    assert (
        result["facts"][0]["review_status"]
        == "needs_review"
    )