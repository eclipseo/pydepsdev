# tests/test_api.py

import pytest
import pytest_asyncio
import aiohttp
from aioresponses import aioresponses

from pydepsdev.api import DepsdevAPI
from pydepsdev.exceptions import APIError
from pydepsdev.utils import encode_url_param
from pydepsdev.constants import BASE_URL

from .mock_responses import (
    GET_PACKAGE_RESPONSE,
    GET_VERSION_RESPONSE,
    GET_REQUIREMENTS_RESPONSE,
    GET_DEPENDENCIES_RESPONSE,
    GET_PROJECT_RESPONSE,
    GET_ADVISORY_RESPONSE,
    GET_QUERY_RESPONSE,
)


@pytest_asyncio.fixture
async def api():
    """
    Provide a DepsdevAPI with fast retry parameters.
    The ClientSession is created inside the running loop.
    """
    client = DepsdevAPI(max_retries=1, base_backoff=0.01, max_backoff=0.01)
    yield client
    await client.close()


@pytest.fixture
def m():
    """Provide an aioresponses mock context."""
    with aioresponses() as mock:
        yield mock


@pytest.mark.asyncio
async def test_get_package_success(api, m):
    pkg = "@colors/colors"
    system = "npm"
    url = f"{BASE_URL}/systems/{system}/packages/{encode_url_param(pkg)}"
    m.get(url, status=200, payload=GET_PACKAGE_RESPONSE)

    result = await api.get_package(system, pkg)
    assert result == GET_PACKAGE_RESPONSE


@pytest.mark.asyncio
async def test_get_package_network_failure(api, m):
    pkg = "foo"
    system = "npm"
    url = f"{BASE_URL}/systems/{system}/packages/{encode_url_param(pkg)}"
    # every attempt times out
    m.get(url, exception=aiohttp.ServerTimeoutError())

    with pytest.raises(APIError) as exc:
        await api.get_package(system, pkg)
    assert "Network failure" in str(exc.value)


@pytest.mark.asyncio
async def test_get_version_success(api, m):
    pkg = "@colors/colors"
    system = "npm"
    version = "1.4.0"
    url = (
        f"{BASE_URL}/systems/{system}"
        f"/packages/{encode_url_param(pkg)}"
        f"/versions/{encode_url_param(version)}"
    )
    m.get(url, status=200, payload=GET_VERSION_RESPONSE)

    result = await api.get_version(system, pkg, version)
    assert result == GET_VERSION_RESPONSE


@pytest.mark.asyncio
async def test_get_requirements_success(api, m):
    system = "nuget"
    pkg = "castle.core"
    version = "5.1.1"
    url = (
        f"{BASE_URL}/systems/{system}"
        f"/packages/{encode_url_param(pkg)}"
        f"/versions/{encode_url_param(version)}:requirements"
    )
    m.get(url, status=200, payload=GET_REQUIREMENTS_RESPONSE)

    result = await api.get_requirements(system, pkg, version)
    assert result == GET_REQUIREMENTS_RESPONSE


@pytest.mark.asyncio
async def test_get_requirements_wrong_system(api):
    with pytest.raises(ValueError):
        await api.get_requirements("npm", "foo", "1.0.0")


@pytest.mark.asyncio
async def test_get_dependencies_success(api, m):
    system = "npm"
    pkg = "@colors/colors"
    version = "1.4.0"
    url = (
        f"{BASE_URL}/systems/{system}"
        f"/packages/{encode_url_param(pkg)}"
        f"/versions/{encode_url_param(version)}:dependencies"
    )
    m.get(url, status=200, payload=GET_DEPENDENCIES_RESPONSE)

    result = await api.get_dependencies(system, pkg, version)
    assert result == GET_DEPENDENCIES_RESPONSE


@pytest.mark.asyncio
async def test_get_project_success(api, m):
    pid = "github.com/pnuckowski/aioresponses"
    url = f"{BASE_URL}/projects/{encode_url_param(pid)}"
    m.get(url, status=200, payload=GET_PROJECT_RESPONSE)

    result = await api.get_project(pid)
    assert result == GET_PROJECT_RESPONSE


@pytest.mark.asyncio
async def test_get_advisory_success(api, m):
    aid = "GHSA-2qrg-x229-3v8q"
    url = f"{BASE_URL}/advisories/{encode_url_param(aid)}"
    m.get(url, status=200, payload=GET_ADVISORY_RESPONSE)

    result = await api.get_advisory(aid)
    assert result == GET_ADVISORY_RESPONSE


@pytest.mark.asyncio
async def test_query_package_versions_success(api, m):
    system = "npm"
    pkg = "react"
    version = "18.2.0"
    qs = (
        f"versionKey.system={system}"
        f"&versionKey.name={encode_url_param(pkg)}"
        f"&versionKey.version={encode_url_param(version)}"
    )
    url = f"{BASE_URL}/query?{qs}"
    m.get(url, status=200, payload=GET_QUERY_RESPONSE)

    result = await api.query_package_versions(
        version_system=system,
        version_name=pkg,
        version=version,
    )
    assert result == GET_QUERY_RESPONSE


@pytest.mark.asyncio
async def test_context_manager_closes_session():
    client = DepsdevAPI(max_retries=0)
    assert not client.session.closed
    async with client:
        pass
    assert client.session.closed
