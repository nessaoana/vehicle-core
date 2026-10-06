"""Validation and normalization rules for Brazilian license plates."""

import re


LICENSE_PLATE_PATTERN = re.compile(r"^[A-Z]{3}(?:\d{4}|\d[A-Z]\d{2})$")


def normalize_license_plate(value: str) -> str:
    """Normalize and validate old-style and Mercosur Brazilian plates."""
    normalized = re.sub(r"[\s-]", "", value).upper()
    if not LICENSE_PLATE_PATTERN.fullmatch(normalized):
        raise ValueError("License plate must use a valid Brazilian format")
    return normalized