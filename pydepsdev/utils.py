import urllib.parse
from typing import NoReturn
from .constants import SUPPORTED_SYSTEMS, SUPPORTED_HASHES


def encode_url_param(param: str) -> str:
    """
    URL-encode a query parameter or path segment.

    Args:
        param (str): The string to be percent-encoded.

    Returns:
        str: A URL-safe, percent-encoded version of `param`.
    """
    return urllib.parse.quote_plus(param)


def validate_system(system: str) -> None:
    """
    Validate that the given system identifier is supported.

    Args:
        system (str): The package system name (e.g. "npm", "pypi") to validate.

    Raises:
        ValueError: If `system` (case-insensitive) is not in SUPPORTED_SYSTEMS.
    """
    normalized = system.upper()
    if normalized not in SUPPORTED_SYSTEMS:
        raise ValueError(
            "This operation is currently only available for "
            f"{', '.join(SUPPORTED_SYSTEMS)}."
        )


def validate_hash(hash_type: str) -> None:
    """
    Validate that the given hash algorithm is supported.

    Args:
        hash_type (str): The hash algorithm name (e.g. "SHA256") to validate.

    Raises:
        ValueError: If `hash_type` (case-insensitive) is not in SUPPORTED_HASHES.
    """
    normalized = hash_type.upper()
    if normalized not in SUPPORTED_HASHES:
        raise ValueError(
            "This operation is currently only available for "
            f"{', '.join(SUPPORTED_HASHES)}."
        )
