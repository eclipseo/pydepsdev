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
from typing import Any, Tuple

from pydepsdev.utils import (
    encode_url_param,
    normalize_package,
    validate_hash,
    validate_system,
)
from pydepsdev.constants import (
    SUPPORTED_SYSTEMS,
    SUPPORTED_SYSTEMS_QUERY,
    SUPPORTED_HASHES,
)


def test_encode_url_param() -> None:
    raw: str = "pkg:npm/%40colors/colors@1.5.0"
    expected: str = urllib.parse.quote_plus(raw)
    assert encode_url_param(raw) == expected


def test_validate_system_valid() -> None:
    for s in SUPPORTED_SYSTEMS:
        validate_system(s)
        validate_system(s.lower())
    # allowed_systems override
    validate_system("npm", allowed_systems=SUPPORTED_SYSTEMS_QUERY)


def test_validate_system_invalid() -> None:
    with pytest.raises(ValueError) as exc:
        validate_system("i_do_not_exist")
    assert "only available for" in str(exc.value)

    with pytest.raises(ValueError):
        validate_system("npm", allowed_systems=["GO"])


def test_validate_hash_valid() -> None:
    for h in SUPPORTED_HASHES:
        validate_hash(h)
        validate_hash(h.lower())


def test_validate_hash_invalid() -> None:
    with pytest.raises(ValueError) as exc:
        validate_hash("SHA1024")
    assert "only available for" in str(exc.value)


@pytest.mark.asyncio
async def test__package_decorator_uppercase() -> None:
    @normalize_package
    async def fn(self: Any, system_name: str, package_name: str) -> Tuple[str, str]:
        return system_name, package_name

    system_name: str
    package_name: str
    system_name, package_name = await fn(None, "npm", "ignored")
    assert system_name == "NPM"
    assert package_name == "ignored"


@pytest.mark.asyncio
async def test_normalize_package_decorator_nuget() -> None:
    @normalize_package
    async def fn(self: Any, system_name: str, package_name: str) -> Tuple[str, str]:
        return system_name, package_name

    system_name: str
    package_name: str
    system_name, package_name = await fn(None, "NuGet", "Foo.Bar_Baz")
    assert system_name == "NUGET"
    # NuGet names are only lowercased, punctuation preserved
    assert package_name == "foo.bar_baz"


@pytest.mark.asyncio
async def test_normalize_package_decorator_pypi() -> None:
    @normalize_package
    async def fn(self: Any, system_name: str, package_name: str) -> Tuple[str, str]:
        return system_name, package_name

    system_name: str
    package_name: str
    system_name, package_name = await fn(None, "PyPI", "My_Pkg.Name")
    assert system_name == "PYPI"
    # PEP503: runs of [-_.] → '-', then lowercase
    assert package_name == "my-pkg-name"


@pytest.mark.asyncio
async def test_normalize_package_decorator_other() -> None:
    @normalize_package
    async def fn(self: Any, system_name: str, package_name: str) -> Tuple[str, str]:
        return system_name, package_name

    system_name: str
    package_name: str
    system_name, package_name = await fn(None, "npm", "SomeName")
    assert system_name == "NPM"
    # other systems: name left untouched
    assert package_name == "SomeName"
