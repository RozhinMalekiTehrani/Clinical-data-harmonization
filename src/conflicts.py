def detect_medication_conflicts(facts):
    medications = [
        fact for fact in facts
        if fact.get("category") == "medication"
    ]

    conflicts = []

    for i in range(len(medications)):
        for j in range(i + 1, len(medications)):

            med_a = medications[i]
            med_b = medications[j]

            name_a = med_a.get("concept", {}).get("display")
            name_b = med_b.get("concept", {}).get("display")

            if name_a and name_b and name_a.lower() != name_b.lower():

                conflicts.append({
                    "type": "medication_conflict",
                    "facts": [name_a, name_b],
                    "status": "needs_review"
                })

                med_a["review_status"] = "needs_review"
                med_b["review_status"] = "needs_review"

    return conflicts