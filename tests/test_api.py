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

import aiohttp
import base64
import pytest
from aioresponses import aioresponses
from urllib.parse import urlencode
from typing import Any, Dict, List, Optional, Tuple, Callable

from pydepsdev.api import DepsdevAPI
from pydepsdev.constants import (
    BASE_URL,
    SUPPORTED_SYSTEMS_REQUIREMENTS,
    SUPPORTED_SYSTEMS_DEPENDENCIES,
    SUPPORTED_SYSTEMS_DEPENDENTS,
    SUPPORTED_SYSTEMS_CAPABILITIES,
    SUPPORTED_SYSTEMS_QUERY,
)
from pydepsdev.utils import encode_url_param
from pydepsdev.exceptions import APIError


def make_url(*segments: str, suffix: str = "") -> str:
    """
    Build a URL by joining segments with '/', appending an optional suffix.
    """
    path = "/".join(segments)
    if suffix:
        path += suffix
    return f"{BASE_URL}/{path}"


@pytest.mark.asyncio
async def test_context_manager_creates_and_closes_session() -> None:
    async with DepsdevAPI() as client:
        assert client.session is not None
    assert client.session is None


@pytest.mark.asyncio
async def test_close_without_open_session() -> None:
    client: DepsdevAPI = DepsdevAPI()
    assert client.session is None
    await client.close()
    assert client.session is None


@pytest.mark.asyncio
async def test_get_package_happy_path(api_client: DepsdevAPI) -> None:
    system: str = "npm"
    package: str = "foo"
    url: str = make_url(
        "systems",
        system.upper(),
        "packages",
        encode_url_param(package),
    )
    payload: Dict[str, Any] = {"name": package}
    with aioresponses() as m:
        m.get(url, payload=payload)
        out: Dict[str, Any] = await api_client.get_package(system, package)
        assert out == payload


@pytest.mark.asyncio
async def test_get_version_happy_path(api_client: DepsdevAPI) -> None:
    system, package, version = "pypi", "bar", "1.2.3"
    url: str = make_url(
        "systems",
        system.upper(),
        "packages",
        encode_url_param(package),
        "versions",
        encode_url_param(version),
    )
    payload: Dict[str, Any] = {"version": version}
    with aioresponses() as m:
        m.get(url, payload=payload)
        out: Dict[str, Any] = await api_client.get_version(system, package, version)
        assert out == payload


# ----- version-batch tests -----
@pytest.mark.asyncio
async def test_get_version_batch_empty(api_client: DepsdevAPI) -> None:
    assert await api_client.get_version_batch([]) == {"responses": []}


@pytest.mark.asyncio
async def test_get_version_batch_too_many(api_client: DepsdevAPI) -> None:
    reqs: List[Tuple[str, str, str]] = [("npm", "package", "1")] * 5001
    with pytest.raises(ValueError):
        await api_client.get_version_batch(reqs)


@pytest.mark.asyncio
async def test_get_version_batch_post(api_client: DepsdevAPI) -> None:
    vr: List[Tuple[str, str, str]] = [("npm", "package", "1.0")]
    url: str = make_url("versionbatch")
    expected_payload: Dict[str, Any] = {
        "requests": [
            {"versionKey": {"system": "npm", "name": "package", "version": "1.0"}}
        ]
    }
    resp: Dict[str, Any] = {"responses": [{"foo": "bar"}], "nextPageToken": "tok"}
    with aioresponses() as m:
        m.post(url, payload=resp)
        out: Dict[str, Any] = await api_client.get_version_batch(vr)
        assert out == resp


@pytest.mark.asyncio
async def test_get_all_versions_batch(
    api_client: DepsdevAPI,
    monkeypatch: Any,
) -> None:
    pages: List[Dict[str, Any]] = [
        {"responses": [{"a": 1}], "nextPageToken": "t"},
        {"responses": [{"b": 2}]},
    ]

    async def fake_batch(
        requests: List[Tuple[str, str, str]],
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        return pages.pop(0)

    monkeypatch.setattr(api_client, "get_version_batch", fake_batch)
    out: List[Dict[str, Any]] = await api_client.get_all_versions_batch(
        [("npm", "package", "1")]
    )
    assert out == [{"a": 1}, {"b": 2}]


# ----- system-limited endpoints -----
@pytest.mark.parametrize(
    "method, system, suffix",
    [
        ("get_requirements", "nuget", ":requirements"),
        ("get_dependencies", "pypi", ":dependencies"),
        ("get_dependents", "cargo", ":dependents"),
        ("get_capabilities", "go", ":capabilities"),
    ],
)
@pytest.mark.asyncio
async def test_system_limited_happy(
    api_client: DepsdevAPI,
    method: str,
    system: str,
    suffix: str,
) -> None:
    package, version = "package", "1.0"
    url: str = make_url(
        "systems",
        system.upper(),
        "packages",
        encode_url_param(package),
        "versions",
        encode_url_param(version),
        suffix=suffix,
    )
    payload: Dict[str, Any] = {"ok": True}
    with aioresponses() as m:
        m.get(url, payload=payload)
        fn: Callable[..., Any] = getattr(api_client, method)
        out: Any = await fn(system, package, version)
        assert out == payload


@pytest.mark.parametrize(
    "method",
    ["get_requirements", "get_dependencies", "get_dependents", "get_capabilities"],
)
@pytest.mark.asyncio
async def test_system_limited_invalid_system(
    api_client: DepsdevAPI,
    method: str,
) -> None:
    fn: Callable[..., Any] = getattr(api_client, method)
    with pytest.raises(ValueError):
        await fn("invalid", "package", "1.0")


# ----- project endpoints -----
@pytest.mark.asyncio
async def test_get_project(api_client: DepsdevAPI) -> None:
    pid: str = "owner/repo"
    url: str = make_url("projects", encode_url_param(pid))
    payload: Dict[str, Any] = {"id": pid}
    with aioresponses() as m:
        m.get(url, payload=payload)
        out: Dict[str, Any] = await api_client.get_project(pid)
        assert out == payload


@pytest.mark.asyncio
async def test_get_project_batch_empty(api_client: DepsdevAPI) -> None:
    assert await api_client.get_project_batch([]) == {"responses": []}


@pytest.mark.asyncio
async def test_get_project_batch_too_many(api_client: DepsdevAPI) -> None:
    ids: List[str] = [str(i) for i in range(5001)]
    with pytest.raises(ValueError):
        await api_client.get_project_batch(ids)


@pytest.mark.asyncio
async def test_get_project_batch_post(api_client: DepsdevAPI) -> None:
    pids: List[str] = ["a", "b"]
    url: str = make_url("projectbatch")
    payload: Dict[str, Any] = {
        "requests": [{"projectKey": {"id": "a"}}, {"projectKey": {"id": "b"}}]
    }
    resp: Dict[str, Any] = {"responses": [{"x": 1}], "nextPageToken": "T"}
    with aioresponses() as m:
        m.post(url, payload=resp)
        out: Dict[str, Any] = await api_client.get_project_batch(pids)
        assert out == resp


@pytest.mark.asyncio
async def test_get_all_projects_batch(
    api_client: DepsdevAPI,
    monkeypatch: Any,
) -> None:
    pages: List[Dict[str, Any]] = [
        {"responses": [{"p": 1}], "nextPageToken": "t"},
        {"responses": [{"q": 2}]},
    ]

    async def fake_batch(
        ids: List[str],
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        return pages.pop(0)

    monkeypatch.setattr(api_client, "get_project_batch", fake_batch)
    out: List[Dict[str, Any]] = await api_client.get_all_projects_batch(["x"])
    assert out == [{"p": 1}, {"q": 2}]


@pytest.mark.asyncio
async def test_get_project_package_versions(api_client: DepsdevAPI) -> None:
    pid: str = "my/repo"
    url: str = make_url("projects", encode_url_param(pid), suffix=":packageversions")
    payload: List[Dict[str, Any]] = [{"version": 1}]
    with aioresponses() as m:
        m.get(url, payload=payload)
        out: List[Dict[str, Any]] = await api_client.get_project_package_versions(pid)
        assert out == payload


# ----- advisory & similarlyNamedPackages -----
@pytest.mark.asyncio
async def test_get_advisory(api_client: DepsdevAPI) -> None:
    advisory: str = "OSV-2023-0001"
    url: str = make_url("advisories", encode_url_param(advisory))
    payload: Dict[str, Any] = {"advisory": advisory}
    with aioresponses() as m:
        m.get(url, payload=payload)
        out: Dict[str, Any] = await api_client.get_advisory(advisory)
        assert out == payload


@pytest.mark.asyncio
async def test_get_similarly_named_packages(api_client: DepsdevAPI) -> None:
    system, package = "npm", "foo"
    url: str = make_url(
        "systems",
        system.upper(),
        "packages",
        encode_url_param(package),
        suffix=":similarlyNamedPackages",
    )
    payload: List[Dict[str, Any]] = [{"name": package}]
    with aioresponses() as m:
        m.get(url, payload=payload)
        out: List[Dict[str, Any]] = await api_client.get_similarly_named_packages(
            system, package
        )
        assert out == payload


# ----- query_package_versions -----
@pytest.mark.asyncio
async def test_query_package_versions_by_hash(api_client: DepsdevAPI) -> None:
    hashtype, hashvalue = "sha256", "abcd"
    url: str = make_url("query")
    b64_hashvalue: str = base64.b64encode(hashvalue.encode("utf-8")).decode("ascii")
    params: Dict[str, str] = {"hash.type": hashtype, "hash.value": b64_hashvalue}
    full_url: str = f"{url}?{urlencode(params)}"

    payload: List[Dict[str, bool]] = [{"h": True}]
    with aioresponses() as m:
        m.get(full_url, payload=payload)
        out: List[Dict[str, Any]] = await api_client.query_package_versions(
            hash_type=hashtype, hash_value=hashvalue
        )
        assert out == payload


@pytest.mark.asyncio
async def test_query_package_versions_by_key(api_client: DepsdevAPI) -> None:
    vs_system, vs_name, vs = "npm", "foo", "1"
    url: str = make_url("query")
    params: Dict[str, str] = {
        "versionKey.system": vs_system.upper(),
        "versionKey.name": vs_name,
        "versionKey.version": vs,
    }
    full_url: str = f"{url}?{urlencode(params)}"

    payload: List[Dict[str, bool]] = [{"k": True}]
    with aioresponses() as m:
        m.get(full_url, payload=payload)
        out: List[Dict[str, Any]] = await api_client.query_package_versions(
            version_system=vs_system,
            version_name=vs_name,
            version=vs,
        )
        assert out == payload


@pytest.mark.asyncio
async def test_query_package_versions_invalid_args(api_client: DepsdevAPI) -> None:
    with pytest.raises(ValueError):
        await api_client.query_package_versions(hash_type="bad", hash_value="x")
    with pytest.raises(ValueError):
        await api_client.query_package_versions(version_system="nobody")


# ----- purl lookups -----
@pytest.mark.asyncio
async def test_get_purl_lookup(api_client: DepsdevAPI) -> None:
    purl: str = "package:npm/name@1.0"
    url: str = make_url("purl", encode_url_param(purl))
    payload: Dict[str, Any] = {"purl": purl}
    with aioresponses() as m:
        m.get(url, payload=payload)
        out: Dict[str, Any] = await api_client.get_purl_lookup(purl)
        assert out == payload


@pytest.mark.asyncio
async def test_get_purl_lookup_batch_empty(api_client: DepsdevAPI) -> None:
    assert await api_client.get_purl_lookup_batch([]) == {"responses": []}


@pytest.mark.asyncio
async def test_get_purl_lookup_batch_too_many(api_client: DepsdevAPI) -> None:
    with pytest.raises(ValueError):
        await api_client.get_purl_lookup_batch(["x"] * 5001)


@pytest.mark.asyncio
async def test_get_purl_lookup_batch_post(api_client: DepsdevAPI) -> None:
    purls: List[str] = ["a", "b"]
    url: str = make_url("purlbatch")
    payload: Dict[str, Any] = {"requests": [{"purl": "a"}, {"purl": "b"}]}
    resp: Dict[str, Any] = {"responses": [{"m": 1}], "nextPageToken": "T"}
    with aioresponses() as m:
        m.post(url, payload=resp)
        out: Dict[str, Any] = await api_client.get_purl_lookup_batch(purls)
        assert out == resp


@pytest.mark.asyncio
async def test_get_all_purl_lookup_batch(
    api_client: DepsdevAPI,
    monkeypatch: Any,
) -> None:
    pages: List[Dict[str, Any]] = [
        {"responses": [{"r": 1}], "nextPageToken": "t"},
        {"responses": [{"s": 2}]},
    ]

    async def fake_batch(
        purls: List[str],
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        return pages.pop(0)

    monkeypatch.setattr(api_client, "get_purl_lookup_batch", fake_batch)
    out: List[Dict[str, Any]] = await api_client.get_all_purl_lookup_batch(["x"])
    assert out == [{"r": 1}, {"s": 2}]


# ----- query_container_images -----
@pytest.mark.asyncio
async def test_query_container_images(api_client: DepsdevAPI) -> None:
    container: str = "chain123"
    url: str = make_url("querycontainerimages", encode_url_param(container))
    payload: Dict[str, List[Dict[str, str]]] = {"results": [{"repo": "abc"}]}
    with aioresponses() as m:
        m.get(url, payload=payload)
        out: Dict[str, List[Dict[str, str]]] = await api_client.query_container_images(
            container
        )
        assert out == payload


# ----- fetch_data error paths -----
@pytest.mark.asyncio
async def test_fetch_data_http_error(api_client: DepsdevAPI) -> None:
    url: str = make_url("systems", "NPM", "packages", "foo")
    with aioresponses() as m:
        m.get(url, status=404, body="Not Found")
        with pytest.raises(APIError) as ei:
            await api_client.fetch_data(url)
    err: APIError = ei.value
    assert err.status == 404
    assert "HTTP error" in err.message


@pytest.mark.asyncio
async def test_fetch_data_server_retry_and_success(monkeypatch: Any) -> None:
    client: DepsdevAPI = DepsdevAPI(max_retries=2, base_backoff=0, max_backoff=0)
    url: str = make_url("test", "retry")
    with aioresponses() as m:
        m.get(url, status=500)
        m.get(url, status=502)
        m.get(url, payload={"ok": True})

        async def no_wait(delay: float) -> None:
            return None

        monkeypatch.setattr("asyncio.sleep", no_wait)
        out: Dict[str, bool] = await client.fetch_data(url)
        assert out == {"ok": True}
    await client.close()


@pytest.mark.asyncio
async def test_fetch_data_network_failure(api_client: DepsdevAPI) -> None:
    url: str = make_url("test", "fail")
    with aioresponses() as m:
        m.get(url, exception=aiohttp.ClientConnectionError("ko"))
        with pytest.raises(APIError) as ei:
            await api_client.fetch_data(url)
    err: APIError = ei.value
    assert err.status is None
    assert "Network failure" in err.message
