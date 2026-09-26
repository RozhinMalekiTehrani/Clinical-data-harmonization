import re
import spacy


def load_nlp():
    nlp = spacy.load("en_core_sci_sm")

    if "negex" not in nlp.pipe_names:
        nlp.add_pipe(
            "negex",
            config={"ent_types": ["ENTITY"]}
        )

    return nlp


def handling_patients_age(text):
    patterns = [
        r"\b(\d{1,3})\s+years?\s+old\b",
        r"\b(\d{1,3})\s*[-]?\s*years?\s*[-]?\s*old\b",
        r"\b(\d{1,3})\s+years?\s+of\s+age\b",
        r"\b(\d{1,3})\s*y\.?\s*o\.?\b",
        r"\b(\d{1,3})\s*y\s*/\s*o\b",
        r"\b(\d{1,3})\s*yrs?\.?\s+old\b",
        r"\bage\s*[:\-]?\s*(\d{1,3})\b",
        r"\baged\s+(\d{1,3})\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())

        if match:
            age = int(match.group(1))

            if 0 <= age <= 120:
                return age

    return None


def extract_entities(text, nlp):
    doc = nlp(text)

    results = []

    for ent in doc.ents:

        is_negated = getattr(ent._, "negex", False)

        results.append({
            "text": ent.text,
            "start_char": ent.start_char,
            "end_char": ent.end_char,
            "is_negated": bool(is_negated)
        })

    return results