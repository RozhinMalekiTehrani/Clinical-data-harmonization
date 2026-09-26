import json
from jsonschema import validate


def validate_canonical_record(record, schema_path):

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    validate(
        instance=record,
        schema=schema
    )

    return True
    