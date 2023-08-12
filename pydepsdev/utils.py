import urllib.parse
from .constants import SUPPORTED_SYSTEMS, SUPPORTED_HASHES


def encode_url_param(param):
    return urllib.parse.quote_plus(param)


def validate_system(system):
    if system.upper() not in SUPPORTED_SYSTEMS:
        raise ValueError(
            f"This operation is currently only available for {', '.join(SUPPORTED_SYSTEMS)}."
        )


def validate_hash(hash_type):
    if hash_type.upper() not in SUPPORTED_HASHES:
        raise ValueError(
            f"This operation is currently only available for {', '.join(SUPPORTED_HASHES)}."
        )
