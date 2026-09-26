def collect_review_items(record):

    review_items = []

    for fact in record.get("facts", []):

        if fact.get("review_status") == "needs_review":

            review_items.append({
                "type": "fact",
                "fact": fact
            })

    return review_items