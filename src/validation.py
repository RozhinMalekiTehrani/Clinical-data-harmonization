import json

from jsonschema import validate


def validate_record(
    record,
    schema_path
):
    with open(
        schema_path,
        "r",
        encoding="utf-8"
    ) as file:
        schema = json.load(file)

    validate(
        instance=record,
        schema=schema
    )

    return True