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
import asyncio
import logging
import random
from typing import Any, Dict, List, Optional, Tuple, Union

from .constants import (
    BASE_URL,
    DEFAULT_BASE_BACKOFF,
    DEFAULT_MAX_BACKOFF,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT_DURATION,
    SUPPORTED_SYSTEMS,
    SUPPORTED_SYSTEMS_REQUIREMENTS,
    SUPPORTED_SYSTEMS_DEPENDENCIES,
    SUPPORTED_SYSTEMS_DEPENDENTS,
    SUPPORTED_SYSTEMS_CAPABILITIES,
    SUPPORTED_SYSTEMS_QUERY,
)
from .exceptions import APIError
from .utils import encode_url_param, validate_hash, validate_system

JSONType = Union[Dict[str, Any], List[Any]]

logger: logging.Logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.WARNING)


class DepsdevAPI:
    session: Optional[aiohttp.ClientSession]
    headers: Dict[str, str]
    timeout_duration: float
    max_retries: int
    base_backoff: float
    max_backoff: float

    def __init__(
        self,
        timeout_duration: float = DEFAULT_TIMEOUT_DURATION,
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_backoff: float = DEFAULT_BASE_BACKOFF,
        max_backoff: float = DEFAULT_MAX_BACKOFF,
    ) -> None:
        """
        Initialize a new Depsdev API client.

        Args:
            timeout_duration (float): Timeout for each request in seconds.
            max_retries (int): Maximum number of retry attempts.
            base_backoff (float): Initial backoff interval in seconds.
            max_backoff (float): Maximum backoff interval in seconds.
        """
        self.session = None
        self.headers = {"Content-Type": "application/json"}
        self.timeout_duration = timeout_duration
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.max_backoff = max_backoff
        logger.debug(
            "DepsdevAPI init timeout=%s retries=%s base_backoff=%s max_backoff=%s",
            timeout_duration,
            max_retries,
            base_backoff,
            max_backoff,
        )

    async def _getsession(self) -> aiohttp.ClientSession:
        """
        Lazily instantiate and return an aiohttp.ClientSession
        within a running event loop.

        Returns:
            aiohttp.ClientSession: The current aiohttp client session.
        """
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self) -> None:
        """
        Close the underlying HTTP session.

        Returns:
            None
        """
        if self.session is not None:
            await self.session.close()
            self.session = None

    async def __aenter__(self) -> "DepsdevAPI":
        """
        Enter the async context. Ensures the session is created.

        Returns:
            DepsdevAPI: The current API client instance.
        """
        await self._getsession()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> None:
        """
        Exit the async context and close session.

        Args:
            exc_type (Optional[type]): Exception type, if raised.
            exc_value (Optional[BaseException]): Exception instance, if raised.
            traceback (Optional[Any]): Traceback object, if exception.

        Returns:
            None
        """
        await self.close()

    async def fetch_data(
        self,
        request_url: str,
        query_params: Optional[Dict[str, str]] = None,
        method: str = "GET",
        json_body: Optional[Any] = None,
    ) -> JSONType:
        """
        Perform an HTTP request (GET, POST, …) with retries and exponential
        backoff. Raises on non-2xx or network failure.

        Args:
            request_url (str): Full URL to send the request to.
            query_params (Optional[Dict[str, str]]): URL query parameters.
            method (str): HTTP method ("GET", "POST", …).
            json_body (Optional[Any]): JSON body for POST/PUT.

        Returns:
            JSONType: Parsed JSON response (dict or list).

        Raises:
            APIError: On HTTP client/server error or network failure.
        """
        session = await self._getsession()
        attempt = 0
        while attempt <= self.max_retries:
            logger.info(
                "Request %s %s params=%s (attempt %s/%s)",
                method,
                request_url,
                query_params,
                attempt + 1,
                self.max_retries + 1,
            )
            try:
                async with session.request(
                    method,
                    request_url,
                    headers=self.headers,
                    params=query_params,
                    json=json_body,
                    timeout=self.timeout_duration,
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    logger.debug("Success %s -> %s", request_url, data)
                    return data

            except aiohttp.ClientResponseError as e:
                status = e.status
                msg = e.message
                if 500 <= status < 600 and attempt < self.max_retries:
                    backoff = min(
                        self.base_backoff * 2**attempt
                        + random.uniform(0, 0.1 * 2**attempt),
                        self.max_backoff,
                    )
                    await asyncio.sleep(backoff)
                    attempt += 1
                else:
                    raise APIError(status, f"HTTP error: {msg}")

            except (aiohttp.ServerTimeoutError, aiohttp.ClientConnectionError) as e:
                if attempt < self.max_retries:
                    backoff = min(
                        self.base_backoff * 2**attempt
                        + random.uniform(0, 0.1 * 2**attempt),
                        self.max_backoff,
                    )
                    await asyncio.sleep(backoff)
                    attempt += 1
                else:
                    raise APIError(None, f"Network failure: {e}")

        raise APIError(None, "Exceeded retry limit")

    def _build_path(self, *segments: str, suffix: str = "") -> str:
        """
        Build a full URL from base + path segments + optional suffix.
        """
        path = "/".join(segments)
        if suffix:
            path += suffix
        return f"{BASE_URL}/{path}"

    async def _get(
        self,
        *segments: str,
        suffix: str = "",
        query_params: Optional[Dict[str, str]] = None,
    ) -> JSONType:
        """
        Internal helper for GET requests.
        """
        url = self._build_path(*segments, suffix=suffix)
        return await self.fetch_data(url, query_params)

    async def _post(
        self, *segments: str, suffix: str = "", json_body: Any = None
    ) -> JSONType:
        """
        Internal helper for POST requests.
        """
        url = self._build_path(*segments, suffix=suffix)
        return await self.fetch_data(url, method="POST", json_body=json_body)

    async def get_package(self, system_name: str, package_name: str) -> JSONType:
        """
        Fetch basic package info including available versions.

        Args:
            system_name (str): Package system (e.g. "NPM", "PYPI").
            package_name (str): Name of the package.

        Returns:
            JSONType: Package info and version list.

        Raises:
            ValueError: If system_name is invalid.
            APIError: On request failure.
        """
        validate_system(system_name)
        name_enc = encode_url_param(package_name)
        return await self._get("systems", system_name, "packages", name_enc)

    async def get_version(
        self, system_name: str, package_name: str, version: str
    ) -> JSONType:
        """
        Fetch detailed info about a specific package version.

        Args:
            system_name (str): Package system (e.g. "NPM", "PYPI").
            package_name (str): Name of the package.
            version (str): Version identifier.

        Returns:
            JSONType: Detailed version metadata.

        Raises:
            ValueError: If system_name is invalid.
            APIError: On request failure.
        """
        validate_system(system_name)
        name_enc = encode_url_param(package_name)
        ver_enc = encode_url_param(version)
        return await self._get(
            "systems",
            system_name,
            "packages",
            name_enc,
            "versions",
            ver_enc,
        )

    async def get_version_batch(
        self,
        version_requests: List[Tuple[str, str, str]],
        page_token: Optional[str] = None,
    ) -> JSONType:
        """
        Perform a batch GetVersion POST, returning one page of results.

        Args:
            version_requests (List[Tuple[str, str, str]]):
                List of (system, name, version) tuples.
            page_token (Optional[str]): Token from a previous response
                for paging.

        Returns:
            JSONType: {
                "responses": [ ... ],
                "nextPageToken": "…"  # if more pages exist
            }

        Raises:
            ValueError: If version_requests is empty or exceeds 5000.
            APIError: On request failure.
        """
        count = len(version_requests)
        if count == 0:
            return {"responses": []}
        if count > 5000:
            raise ValueError("version_requests may not exceed 5000 entries")

        payload: Dict[str, Any] = {"requests": []}
        for system, pkg, ver in version_requests:
            validate_system(system)
            payload["requests"].append(
                {
                    "versionKey": {
                        "system": system,
                        "name": pkg,
                        "version": ver,
                    }
                }
            )
        if page_token:
            payload["pageToken"] = page_token

        return await self._post("versionbatch", json_body=payload)

    async def get_all_versions_batch(
        self, version_requests: List[Tuple[str, str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Convenience wrapper to retrieve all pages for a given batch.

        Args:
            version_requests (List[Tuple[str, str, str]]):
                List of (system, name, version) tuples.

        Returns:
            List[Dict[str, Any]]: All version info dicts across pages.

        Raises:
            ValueError: If version_requests exceeds 5000.
            APIError: On request failure.
        """
        all_responses: List[Dict[str, Any]] = []
        next_token: Optional[str] = None
        while True:
            resp = await self.get_version_batch(version_requests, next_token)
            all_responses.extend(resp.get("responses", []))
            next_token = resp.get("nextPageToken")
            if not next_token:
                break
        return all_responses

    async def get_requirements(
        self, system_name: str, package_name: str, version: str
    ) -> JSONType:
        """
        Fetch declared requirements for a NuGet package version.

        Args:
            system_name (str): Must be "NUGET".
            package_name (str): Name of the package.
            version (str): Version identifier.

        Returns:
            JSONType: Requirements list or tree.

        Raises:
            ValueError: If system_name is not "NUGET".
            APIError: On request failure.
        """
        validate_system(system_name, SUPPORTED_SYSTEMS_REQUIREMENTS)
        name_enc = encode_url_param(package_name)
        ver_enc = encode_url_param(version)
        return await self._get(
            "systems",
            system_name,
            "packages",
            name_enc,
            "versions",
            ver_enc,
            suffix=":requirements",
        )

    async def get_dependencies(
        self, system_name: str, package_name: str, version: str
    ) -> JSONType:
        """
        Fetch resolved dependency graph for a package version.

        Args:
            system_name (str): Package system identifier.
            package_name (str): Name of the package.
            version (str): Version identifier.

        Returns:
            JSONType: Dependency graph structure.

        Raises:
            ValueError: If system_name is invalid.
            APIError: On request failure.
        """
        validate_system(system_name, SUPPORTED_SYSTEMS_DEPENDENCIES)
        name_enc = encode_url_param(package_name)
        ver_enc = encode_url_param(version)
        return await self._get(
            "systems",
            system_name,
            "packages",
            name_enc,
            "versions",
            ver_enc,
            suffix=":dependencies",
        )

    async def get_dependents(
        self, system_name: str, package_name: str, version: str
    ) -> JSONType:
        """
        Fetch dependent counts for a specific package version.

        Args:
            system_name (str): Package system (e.g. "NPM", "PYPI").
            package_name (str): Name of the package.
            version (str): Version identifier.

        Returns:
            JSONType: {
                "dependentCount": int,
                "directDependentCount": int,
                "indirectDependentCount": int
            }

        Raises:
            ValueError: If system_name is invalid.
            APIError: On request failure.
        """
        validate_system(system_name, SUPPORTED_SYSTEMS_DEPENDENTS)
        name_enc = encode_url_param(package_name)
        ver_enc = encode_url_param(version)
        return await self._get(
            "systems",
            system_name,
            "packages",
            name_enc,
            "versions",
            ver_enc,
            suffix=":dependents",
        )

    async def get_capabilities(
        self, system_name: str, package_name: str, version: str
    ) -> JSONType:
        """
        Fetch Capslock capability call counts for a specific package
        version. Currently only available for Go.

        Args:
            system_name (str): Must be "GO".
            package_name (str): Name of the package.
            version (str): Version identifier.

        Returns:
            JSONType: {
                "capabilities": [
                    {
                        "capability": str,
                        "directCount": int,
                        "indirectCount": int
                    },
                    ...
                ]
            }

        Raises:
            ValueError: If system_name is not "GO".
            APIError: On request failure.
        """
        validate_system(system_name, SUPPORTED_SYSTEMS_CAPABILITIES)
        name_enc = encode_url_param(package_name)
        ver_enc = encode_url_param(version)
        return await self._get(
            "systems",
            system_name,
            "packages",
            name_enc,
            "versions",
            ver_enc,
            suffix=":capabilities",
        )

    async def get_project(self, project_id: str) -> JSONType:
        """
        Fetch metadata about a source-control project.

        Args:
            project_id (str): Repository identifier or URL.

        Returns:
            JSONType: Project metadata.

        Raises:
            APIError: On request failure.
        """
        id_enc = encode_url_param(project_id)
        return await self._get("projects", id_enc)

    async def get_project_batch(
        self,
        project_ids: List[str],
        page_token: Optional[str] = None,
    ) -> JSONType:
        """
        Perform a batch GetProject POST, returning one page of results.

        Args:
            project_ids (List[str]):
                List of project identifiers.
            page_token (Optional[str]): Token from a previous response
                for paging.

        Returns:
            JSONType: {
                "responses": [ ... ],
                "nextPageToken": "…"  # if more pages exist
            }

        Raises:
            ValueError: If project_ids is empty or exceeds 5000 entries.
            APIError: On request failure.
        """
        count = len(project_ids)
        if count == 0:
            return {"responses": []}
        if count > 5000:
            raise ValueError("project_ids may not exceed 5000 entries")

        payload: Dict[str, Any] = {"requests": []}
        for pid in project_ids:
            payload["requests"].append({"projectKey": {"id": pid}})
        if page_token:
            payload["pageToken"] = page_token

        return await self._post("projectbatch", json_body=payload)

    async def get_all_projects_batch(
        self,
        project_ids: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Convenience wrapper to retrieve all pages for a given project
        batch.

        Args:
            project_ids (List[str]): List of project identifiers.

        Returns:
            List[Dict[str, Any]]: All project metadata dicts across pages.

        Raises:
            ValueError: If project_ids exceeds 5000 entries.
            APIError: On request failure.
        """
        all_responses: List[Dict[str, Any]] = []
        next_token: Optional[str] = None
        while True:
            resp = await self.get_project_batch(project_ids, next_token)
            all_responses.extend(resp.get("responses", []))
            next_token = resp.get("nextPageToken")
            if not next_token:
                break
        return all_responses

    async def get_project_package_versions(self, project_id: str) -> JSONType:
        """
        Fetch package versions derived from a project.

        Args:
            project_id (str): Repository identifier or URL.

        Returns:
            JSONType: List of package version entries.

        Raises:
            APIError: On request failure.
        """
        id_enc = encode_url_param(project_id)
        return await self._get("projects", id_enc, suffix=":packageversions")

    async def get_advisory(self, advisory_id: str) -> JSONType:
        """
        Fetch details of a security advisory by OSV ID.

        Args:
            advisory_id (str): Advisory identifier.

        Returns:
            JSONType: Advisory metadata.

        Raises:
            APIError: On request failure.
        """
        id_enc = encode_url_param(advisory_id)
        return await self._get("advisories", id_enc)

    async def get_similarly_named_packages(
        self, system_name: str, package_name: str
    ) -> JSONType:
        """
        Fetch packages with names similar to the requested package.

        Args:
            system_name (str): Package system (e.g. "NPM", "PYPI").
            package_name (str): Name of the package.

        Returns:
            JSONType: List of similarly-named packageKey objects.

        Raises:
            ValueError: If system_name is invalid.
            APIError: On request failure.
        """
        validate_system(system_name)
        name_enc = encode_url_param(package_name)
        return await self._get(
            "systems",
            system_name,
            "packages",
            name_enc,
            suffix=":similarlyNamedPackages",
        )

    async def query_package_versions(
        self,
        hash_type: Optional[str] = None,
        hash_value: Optional[str] = None,
        version_system: Optional[str] = None,
        version_name: Optional[str] = None,
        version: Optional[str] = None,
    ) -> JSONType:
        """
        Query package versions by content hash or version key.

        Args:
            hash_type (Optional[str]): Hash algorithm (e.g. "SHA256").
            hash_value (Optional[str]): Package file hash value.
            version_system (Optional[str]): System for version key.
            version_name (Optional[str]): Name field of version key.
            version (Optional[str]): Version field of version key.

        Returns:
            JSONType: Matching package version entries.

        Raises:
            ValueError: If hash_type or version_system is invalid.
            APIError: On request failure.
        """
        if hash_type and hash_value:
            validate_hash(hash_type)
        if version_system:
            validate_system(version_system, SUPPORTED_SYSTEMS_QUERY)

        params: Dict[str, str] = {}
        if hash_type and hash_value:
            params["hash.type"] = hash_type
            params["hash.value"] = hash_value
        if version_system:
            params["versionKey.system"] = version_system
        if version_name:
            params["versionKey.name"] = version_name
        if version:
            params["versionKey.version"] = version

        return await self._get("query", query_params=params)

    async def get_purl_lookup(self, purl: str) -> JSONType:
        """
        Search for a package or package version specified via purl.

        For a package lookup, the purl is of the form
        pkg:type/namespace/name or pkg:type/name. For a version lookup,
        append @version. All special characters must be percent-encoded.

        Args:
            purl (str): The purl to look up, e.g.
                "pkg:npm/%40colors/colors" or
                "pkg:npm/%40colors/colors@1.5.0".

        Returns:
            JSONType: The JSON response from GetPackage or GetVersion.

        Raises:
            APIError: On HTTP client/server error or network failure.
        """
        enc = encode_url_param(purl)
        return await self._get("purl", enc)

    async def get_purl_lookup_batch(
        self, purls: List[str], page_token: Optional[str] = None
    ) -> JSONType:
        """
        Perform a batch PurlLookup POST, returning one page of results.

        Args:
            purls (List[str]): List of purls (must include @version).
            page_token (Optional[str]): Token from a previous response
                for paging.

        Returns:
            JSONType: {
                "responses": [ ... ],
                "nextPageToken": "…"  # if more pages exist
            }

        Raises:
            ValueError: If purls is empty or exceeds 5000 entries.
            APIError: On request failure.
        """
        count = len(purls)
        if count == 0:
            return {"responses": []}
        if count > 5000:
            raise ValueError("purls may not exceed 5000 entries")

        payload: Dict[str, Any] = {"requests": []}
        for p in purls:
            payload["requests"].append({"purl": p})
        if page_token:
            payload["pageToken"] = page_token

        return await self._post("purlbatch", json_body=payload)

    async def get_all_purl_lookup_batch(self, purls: List[str]) -> List[Dict[str, Any]]:
        """
        Convenience wrapper to retrieve all pages for a given PurlLookup
        batch.

        Args:
            purls (List[str]): List of purls (must include @version).

        Returns:
            List[Dict[str, Any]]: All lookup responses across pages.

        Raises:
            ValueError: If purls exceeds 5000 entries.
            APIError: On request failure.
        """
        all_responses: List[Dict[str, Any]] = []
        next_token: Optional[str] = None
        while True:
            resp = await self.get_purl_lookup_batch(purls, next_token)
            all_responses.extend(resp.get("responses", []))
            next_token = resp.get("nextPageToken")
            if not next_token:
                break
        return all_responses

    async def query_container_images(self, chain_id: str) -> JSONType:
        """
        Search for container image repositories on DockerHub that match the
        requested OCI Chain ID. At most 1000 image repositories are returned.

        Args:
            chain_id (str): An OCI Chain ID referring to an ordered sequence
                of OCI layers.

        Returns:
            JSONType: {
                "results": [
                    { "repository": str },
                    …
                ]
            }

        Raises:
            APIError: On request failure.
        """
        enc = encode_url_param(chain_id)
        return await self._get("querycontainerimages", enc)
