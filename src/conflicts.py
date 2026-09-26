def detect_medication_conflicts(facts):
    medications = [
        fact
        for fact in facts
        if fact.get("category") == "medication"
        and fact.get("assertion") == "present"
        or (
            fact.get("category") == "medication"
            and fact.get("assertion") == "uncertain"
        )
    ]

    names = {
        fact.get("concept", {}).get("display", "").lower()
        for fact in medications
    }

    conflicts = []

    if (
        "apixaban" in names
        and "rivaroxaban" in names
    ):

        conflict = {
            "type": "medication_conflict",
            "status": "needs_review",
            "facts": [
                "apixaban",
                "rivaroxaban"
            ],
            "reason": (
                "Different medication sources contain "
                "apixaban and rivaroxaban; the pipeline "
                "does not choose between them."
            )
        }

        conflicts.append(conflict)

        for fact in medications:
            if fact.get(
                "concept",
                {}
            ).get("display", "").lower() in {
                "apixaban",
                "rivaroxaban"
            }:
                fact["review_status"] = (
                    "needs_review"
                )

    return conflicts