def map_lab_code(local_code, mapping):
    if not local_code:
        return None

    return mapping.get(
        "lab_codes",
        {}
    ).get(local_code)


def normalize_unit(test_name, unit, mapping):
    if not unit:
        return None

    unit_config = (
        mapping
        .get("unit_conversions", {})
        .get(test_name, {})
        .get(unit)
    )

    if unit_config is None:
        return {
            "canonical_unit": unit,
            "factor": 1.0,
            "offset": 0.0
        }

    return unit_config


def normalize_numeric_value(
    value,
    unit_config
):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return (
        number * unit_config["factor"]
        + unit_config["offset"]
    )