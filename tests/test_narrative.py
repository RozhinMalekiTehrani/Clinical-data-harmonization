import spacy

from src.narrative import (
    extract_age,
    process_narrative
)


def test_age_extraction():

    text = (
        "The patient is 45 years old."
    )

    result = extract_age(text)

    assert result["age"] == 45


def test_narrative_required_cases():

    nlp = spacy.load(
        "en_core_sci_sm"
    )

    text = """
    Document N-204, recorded 2026-08-12:
    Patient denies chest pain.
    Shortness of breath occurs only when climbing
    two flights.
    Apixaban 5 mg twice daily; last dose yesterday evening.
    Creatinine 1.6 mg/dL on 11 Aug 2026.
    An older imported medication list shows rivaroxaban.
    Medication reconciliation is required.
    """

    result = process_narrative(
        text,
        "note_N204.txt",
        nlp
    )

    facts = result["facts"]

    chest_pain = [
        fact for fact in facts
        if fact["concept"]["display"]
        == "chest pain"
    ]

    assert len(chest_pain) == 1

    assert (
        chest_pain[0]["assertion"]
        == "absent"
    )

    medications = [
        fact for fact in facts
        if fact["category"] == "medication"
    ]

    medication_names = {
        fact["concept"]["display"]
        for fact in medications
    }

    assert "apixaban" in medication_names
    assert "rivaroxaban" in medication_names

    creatinine = [
        fact for fact in facts
        if fact["concept"]["display"]
        == "Creatinine"
    ]

    assert len(creatinine) == 1
    assert creatinine[0]["value"]["number"] == 1.6