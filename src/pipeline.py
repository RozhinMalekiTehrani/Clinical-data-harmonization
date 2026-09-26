from .conflicts import detect_medication_conflicts
from .review_queue import build_review_queue
from .structured import process_csv_record
from .narrative import process_narrative
from .validation import validate_record


def run_pipeline(
    structured_records,
    narrative_text,
    mapping,
    structured_document_id,
    narrative_document_id,
    schema_path,
    nlp
):

    all_facts = []

    structured_records_output = []

    for index, record in enumerate(
        structured_records
    ):

        result = process_csv_record(
            record=record,
            row_index=index,
            document_id=structured_document_id,
            mapping=mapping
        )

        structured_records_output.append(
            result
        )

        all_facts.extend(
            result["facts"]
        )

    narrative_output = process_narrative(
        text=narrative_text,
        document_id=narrative_document_id,
        nlp=nlp
    )

    all_facts.extend(
        narrative_output["facts"]
    )

    conflicts = detect_medication_conflicts(
        all_facts
    )

    quality = {
        "missing": [],
        "unknown": [],
        "not_mentioned": [],
        "conflicting": conflicts,
        "missing_required": [],
        "conflicts": conflicts,
        "warnings": []
    }

    for result in structured_records_output:

        result_quality = result["quality"]

        quality["missing_required"].extend(
            result_quality["missing_required"]
        )

        quality["unknown"].extend(
            result_quality["unknown"]
        )

    for fact in all_facts:

        if fact.get("assertion") == "uncertain":
            quality["warnings"].append(
                "uncertain_assertion_present"
            )

    canonical_record = {
        "schema_version": "1.0",
        "patient": {
            "source_patient_id": (
                structured_records[0].get(
                    "patient_id"
                )
                if structured_records
                else None
            ),
            "birth_date": None
        },
        "encounter": {
            "source_encounter_id": None,
            "event_time": (
                structured_records[0].get(
                    "result_time"
                )
                if structured_records
                else None
            )
        },
        "facts": all_facts,
        "quality": quality
    }

    validate_record(
        canonical_record,
        schema_path
    )

    review_queue = build_review_queue(
        canonical_record
    )

    return {
        "canonical_record": canonical_record,
        "review_queue": review_queue
    }