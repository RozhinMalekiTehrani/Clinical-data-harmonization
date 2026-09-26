def map_local_lab_code(local_code, mapping):
    """
    Map an organization-specific laboratory code.

    Returns None if no mapping exists.
    The system never guesses an unknown code.
    """

    return mapping.get("lab_codes", {}).get(local_code)


def normalize_unit(concept_display, unit, mapping):
    """
    Normalize a unit only when an explicit configuration rule exists.
    """

    if not unit:
        return None

    unit_config = (
        mapping.get("unit_conversions", {})
        .get(concept_display.lower(), {})
        .get(unit)
    )

    if unit_config is None:
        return None

    return unit_config["canonical_unit"]