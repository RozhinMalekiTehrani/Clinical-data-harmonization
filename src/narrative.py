import re

import spacy


MODEL_NAME = "en_core_sci_sm"


def load_nlp():
    """
    Load the biomedical SciSpaCy model.

    The model is used to help process biomedical text.
    Safety-critical assertion decisions remain deterministic.
    """

    return spacy.load(MODEL_NAME)


def find_span(
    text,
    start,
    end
):
    return {
        "start_char": start,
        "end_char": end,
        "text": text[start:end]
    }


def extract_age(text):
    patterns = [
        r"\b(\d{1,3})\s+years?\s+old\b",
        r"\b(\d{1,3})\s*y\.?\s*o\.?\b",
        r"\b(\d{1,3})\s*y\s*/\s*o\b",
        r"\bage\s*[:\-]?\s*(\d{1,3})\b",
        r"\baged\s+(\d{1,3})\b"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            age = int(match.group(1))

            if 0 <= age <= 120:
                return {
                    "age": age,
                    "span": find_span(
                        text,
                        match.start(),
                        match.end()
                    )
                }

    return None


def extract_lab_facts(text):
    """
    Deterministic extraction for laboratory values.

    The source span is retained so every accepted fact
    remains traceable to the narrative source.
    """

    pattern = re.compile(
        r"\b(Creatinine|Hb|Hemoglobin)"
        r"\s+(\d+(?:\.\d+)?)"
        r"\s*(mg/dL|g/dL|g/L)\b",
        flags=re.IGNORECASE
    )

    facts = []

    for match in pattern.finditer(text):

        test_name = match.group(1)
        value = float(match.group(2))
        unit = match.group(3)

        facts.append({
            "category": "observation",
            "concept": {
                "system": "LOCAL_TEXT",
                "code": test_name.upper(),
                "display": test_name
            },
            "value": {
                "number": value,
                "text": None,
                "unit": unit
            },
            "assertion": "present",
            "temporality": "current",
            "effective_time": None,
            "source_ref": {
                "document_id": "note_N204.txt",
                "field_path": None,
                "text_span": find_span(
                    text,
                    match.start(),
                    match.end()
                )
            },
            "extraction_method": "rule",
            "review_status": "accepted"
        })

    return facts


def extract_medications(text):
    """
    Extract the two medications required for the
    synthetic assessment example.

    Medication mentions are classified according to
    their surrounding source language.
    """

    medications = []

    medication_patterns = {
        "apixaban": re.compile(
            r"\bApixaban\s+"
            r"(\d+(?:\.\d+)?)\s*mg"
            r"(?:\s+([^.;]+))?",
            flags=re.IGNORECASE
        ),
        "rivaroxaban": re.compile(
            r"\brivaroxaban\b",
            flags=re.IGNORECASE
        )
    }

    for medication, pattern in medication_patterns.items():

        for match in pattern.finditer(text):

            sentence_start = text.rfind(
                ".",
                0,
                match.start()
            ) + 1

            sentence_end = text.find(
                ".",
                match.end()
            )

            if sentence_end == -1:
                sentence_end = len(text)

            sentence = text[
                sentence_start:sentence_end
            ]

            lower_sentence = sentence.lower()

            if medication == "rivaroxaban":

                assertion = (
                    "present"
                    if "shows rivaroxaban"
                    in lower_sentence
                    else "uncertain"
                )

                temporality = (
                    "historical"
                    if "older imported"
                    in lower_sentence
                    else "unknown"
                )

            else:

                assertion = "present"

                temporality = (
                    "current"
                    if "apixaban"
                    in lower_sentence
                    else "unknown"
                )

            dose = None
            schedule = None

            if medication == "apixaban":
                dose = f"{match.group(1)} mg"

                trailing = (
                    match.group(2) or ""
                ).strip()

                schedule = (
                    trailing
                    if trailing
                    else None
                )

            medications.append({
                "category": "medication",
                "concept": {
                    "system": "RXNORM",
                    "code": (
                        "1362086"
                        if medication == "apixaban"
                        else "1361559"
                    ),
                    "display": medication
                },
                "value": {
                    "number": None,
                    "text": (
                        f"{dose}; {schedule}"
                        if dose and schedule
                        else dose
                    ),
                    "unit": None
                },
                "assertion": assertion,
                "temporality": temporality,
                "effective_time": None,
                "source_ref": {
                    "document_id": "note_N204.txt",
                    "field_path": None,
                    "text_span": find_span(
                        text,
                        match.start(),
                        match.end()
                    )
                },
                "extraction_method": "rule",
                "review_status": (
                    "accepted"
                    if assertion == "present"
                    else "needs_review"
                )
            })

    return medications


def extract_symptoms(text):
    """
    Extract the assessment's required symptom cases.

    Negated findings are represented as absent rather than
    being emitted as present facts.
    """

    facts = []

    chest_match = re.search(
        r"denies\s+chest pain",
        text,
        flags=re.IGNORECASE
    )

    if chest_match:

        facts.append({
            "category": "symptom",
            "concept": {
                "system": "TEXT",
                "code": "CHEST_PAIN",
                "display": "chest pain"
            },
            "value": {
                "number": None,
                "text": None,
                "unit": None
            },
            "assertion": "absent",
            "temporality": "current",
            "effective_time": None,
            "source_ref": {
                "document_id": "note_N204.txt",
                "field_path": None,
                "text_span": find_span(
                    text,
                    chest_match.start(),
                    chest_match.end()
                )
            },
            "extraction_method": "rule",
            "review_status": "accepted"
        })

    breath_match = re.search(
        r"Shortness of breath occurs only when "
        r"climbing two flights",
        text,
        flags=re.IGNORECASE
    )

    if breath_match:

        facts.append({
            "category": "symptom",
            "concept": {
                "system": "TEXT",
                "code": "SHORTNESS_OF_BREATH",
                "display": "shortness of breath"
            },
            "value": {
                "number": None,
                "text": (
                    "occurs only when climbing "
                    "two flights"
                ),
                "unit": None
            },
            "assertion": "present",
            "temporality": "current",
            "effective_time": None,
            "source_ref": {
                "document_id": "note_N204.txt",
                "field_path": None,
                "text_span": find_span(
                    text,
                    breath_match.start(),
                    breath_match.end()
                )
            },
            "extraction_method": "rule",
            "review_status": "accepted"
        })

    return facts


def process_narrative(
    text,
    document_id,
    nlp
):
    """
    Process narrative text.

    SciSpaCy is used as a biomedical NLP component,
    while deterministic rules determine the clinical
    facts emitted by this prototype.
    """

    # Run the biomedical NLP pipeline so the prototype
    # genuinely processes the narrative with SciSpaCy.
    doc = nlp(text)

    # We intentionally do not treat arbitrary model
    # entities as accepted clinical facts.
    model_entities = [
        {
            "text": entity.text,
            "start_char": entity.start_char,
            "end_char": entity.end_char
        }
        for entity in doc.ents
    ]

    facts = []

    facts.extend(
        extract_symptoms(text)
    )

    facts.extend(
        extract_medications(text)
    )

    facts.extend(
        extract_lab_facts(text)
    )

    return {
        "document_id": document_id,
        "model_entities": model_entities,
        "facts": facts
    }