def build_review_queue(record):
    queue = []

    for fact in record.get("facts", []):

        if fact.get("review_status") == "needs_review":

            queue.append({
                "type": "fact",
                "reason": "fact_requires_review",
                "fact": fact
            })

    for conflict in record.get(
        "quality",
        {}
    ).get("conflicts", []):

        queue.append({
            "type": "conflict",
            "reason": "source_conflict",
            "conflict": conflict
        })

    return queue