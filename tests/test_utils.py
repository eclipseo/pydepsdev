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
import pytest

from pydepsdev.utils import encode_url_param, validate_system, validate_hash
from pydepsdev.constants import (
    SUPPORTED_SYSTEMS,
    SUPPORTED_SYSTEMS_QUERY,
    SUPPORTED_HASHES,
)


def test_encode_url_param():
    raw = "pkg:npm/%40colors/colors@1.5.0"
    assert encode_url_param(raw) == urllib.parse.quote_plus(raw)


def test_validate_system_valid():
    for s in SUPPORTED_SYSTEMS:
        validate_system(s)
        validate_system(s.lower())
    validate_system("npm", allowed_systems=SUPPORTED_SYSTEMS_QUERY)


def test_validate_system_invalid():
    with pytest.raises(ValueError) as exc:
        validate_system("i_do_not_exist")
    assert "only available for" in str(exc.value)

    with pytest.raises(ValueError):
        validate_system("npm", allowed_systems=["GO"])


def test_validate_hash_valid():
    for h in SUPPORTED_HASHES:
        validate_hash(h)
        validate_hash(h.lower())


def test_validate_hash_invalid():
    with pytest.raises(ValueError) as exc:
        validate_hash("SHA1024")
    assert "only available for" in str(exc.value)
