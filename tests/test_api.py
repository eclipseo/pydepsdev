import pytest
import json
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


@pytest.mark.asyncio
async def test_get_package_success():
    package_name = "@colors/colors"
    encoded_package_name = encode_url_param(package_name)
    system = "npm"

    with aioresponses() as m:
        url = f"{BASE_URL}/systems/{system}/packages/{encoded_package_name}"
        m.get(url, status=200, payload=GET_PACKAGE_RESPONSE)

        async with DepsdevAPI() as api:
            result = await api.get_package(system, package_name)
            assert result == GET_PACKAGE_RESPONSE


@pytest.mark.asyncio
async def test_get_package_timeout_and_retries():
    package_name = "@colors/colors"
    encoded_package_name = encode_url_param(package_name)
    system = "npm"

    with aioresponses() as m:
        url = f"{BASE_URL}/systems/{system}/packages/{encoded_package_name}"
        # Simulating timeout
        m.get(url, exception=aiohttp.ServerTimeoutError())

        async with DepsdevAPI(max_retries=2, base_backoff=0.01) as api:
            with pytest.raises(APIError) as exc_info:
                await api.get_package(system, package_name)
            assert "Failed after 2 retries" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_version_success():
    package_name = "@colors/colors"
    encoded_package_name = encode_url_param(package_name)
    version = "1.4.0"
    system = "npm"

    with aioresponses() as m:
        url = f"{BASE_URL}/systems/{system}/packages/{encoded_package_name}/versions/{version}"
        m.get(url, status=200, payload=GET_VERSION_RESPONSE)

        async with DepsdevAPI() as api:
            result = await api.get_version(system, package_name, version)
            assert result == GET_VERSION_RESPONSE


@pytest.mark.asyncio
async def test_get_requirements_success():
    system = "nuget"
    package_name = "castle.core"
    encoded_package_name = encode_url_param(package_name)
    version = "5.1.1"

    with aioresponses() as m:
        encoded_version = encode_url_param(version)
        url = f"{BASE_URL}/systems/{system}/packages/{encoded_package_name}/versions/{version}:requirements"
        m.get(url, status=200, payload=GET_REQUIREMENTS_RESPONSE)

        async with DepsdevAPI() as api:
            result = await api.get_requirements(system, package_name, version)
            assert result == GET_REQUIREMENTS_RESPONSE


@pytest.mark.asyncio
async def test_get_requirements_wrong_system():
    with pytest.raises(ValueError) as exc_info:
        async with DepsdevAPI() as api:
            await api.get_requirements("npm", "somepackage", "1.0.0")
        assert "currently only available for NuGet" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_dependencies_success():
    system = "npm"
    package_name = "@colors/colors"
    encoded_package_name = encode_url_param(package_name)
    version = "1.4.0"

    with aioresponses() as m:
        url = f"{BASE_URL}/systems/{system}/packages/{encoded_package_name}/versions/{version}:dependencies"
        m.get(url, status=200, payload=GET_DEPENDENCIES_RESPONSE)

        async with DepsdevAPI() as api:
            result = await api.get_dependencies(system, package_name, version)
            assert result == GET_DEPENDENCIES_RESPONSE


@pytest.mark.asyncio
async def test_get_project_success():
    project_id = "github.com/pnuckowski/aioresponses"
    encoded_project_id = encode_url_param(project_id)

    with aioresponses() as m:
        url = f"{BASE_URL}/projects/{encoded_project_id}"
        m.get(url, status=200, payload=GET_PROJECT_RESPONSE)

        async with DepsdevAPI() as api:
            result = await api.get_project(project_id)
            assert result == GET_PROJECT_RESPONSE


@pytest.mark.asyncio
async def test_get_advisory_success():
    advisory_id = "GHSA-2qrg-x229-3v8q"
    encoded_advisory_id = encode_url_param(advisory_id)

    with aioresponses() as m:
        url = f"{BASE_URL}/advisories/{encoded_advisory_id}"
        m.get(url, status=200, payload=GET_ADVISORY_RESPONSE)

        async with DepsdevAPI() as api:
            result = await api.get_advisory(advisory_id)
            assert result == GET_ADVISORY_RESPONSE


@pytest.mark.asyncio
async def test_query_package_versions_success():
    package_name = "@colors/colors"
    encoded_package_name = encode_url_param(package_name)
    system = "npm"
    version = "18.2.0"

    with aioresponses() as m:
        url = f"{BASE_URL}/query?versionKey.name={encoded_package_name}&versionKey.system={system}&versionKey.version={version}"
        m.get(url, status=200, payload=GET_QUERY_RESPONSE)

        async with DepsdevAPI() as api:
            result = await api.query_package_versions(
                version_system=system, version_name=package_name, version=version
            )
            assert result == GET_QUERY_RESPONSE


@pytest.mark.asyncio
async def test_session_closing():
    async with DepsdevAPI() as api:
        assert not api.session.closed

    assert api.session.closed
