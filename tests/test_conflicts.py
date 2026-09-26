from src.conflicts import (
    detect_medication_conflicts
)


def test_apixaban_rivaroxaban_conflict():

    facts = [
        {
            "category": "medication",
            "concept": {
                "display": "apixaban"
            },
            "assertion": "present",
            "review_status": "accepted"
        },
        {
            "category": "medication",
            "concept": {
                "display": "rivaroxaban"
            },
            "assertion": "present",
            "review_status": "accepted"
        }
    ]

    conflicts = detect_medication_conflicts(
        facts
    )

    assert len(conflicts) == 1

    assert (
        conflicts[0]["status"]
        == "needs_review"
    )

    assert all(
        fact["review_status"]
        == "needs_review"
        for fact in facts
    )