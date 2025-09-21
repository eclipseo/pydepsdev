# SPDX-License-Identifier: Apache-2.0
#
# Copyright 2023-2025 Robert-André Mauchin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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
