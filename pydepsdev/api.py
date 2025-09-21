import aiohttp
import asyncio
import logging
import random
from typing import Any, Dict, List, Optional, Union

from .constants import (
    BASE_URL,
    DEFAULT_BASE_BACKOFF,
    DEFAULT_MAX_BACKOFF,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT_DURATION,
)
from .exceptions import APIError
from .utils import encode_url_param, validate_hash, validate_system

# A JSON‐like payload: either a dict or a list
JSONType = Union[Dict[str, Any], List[Any]]

logger: logging.Logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.WARNING)


class DepsdevAPI:
    session: aiohttp.ClientSession
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
        self.session = aiohttp.ClientSession()
        self.headers = {"Content-Type": "application/json"}
        self.timeout_duration = timeout_duration
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.max_backoff = max_backoff

        logger.debug(
            "DepsdevAPI initialized with timeout=%s, retries=%s, base_backoff=%s, max_backoff=%s",
            timeout_duration,
            max_retries,
            base_backoff,
            max_backoff,
        )

    async def close(self) -> None:
        """Shut down the underlying HTTP session."""
        await self.session.close()

    async def __aenter__(self) -> "DepsdevAPI":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> None:
        await self.close()

    async def fetch_data(
        self,
        request_url: str,
        query_params: Optional[Dict[str, str]] = None,
    ) -> JSONType:
        """
        Perform GET with retries/backoff, returning parsed JSON.
        Raises APIError on client (4xx) or server (5xx) failures.
        """
        attempt_count: int = 0

        while attempt_count <= self.max_retries:
            logger.info(
                "Requesting %s with params %s (attempt %s/%s)",
                request_url,
                query_params,
                attempt_count + 1,
                self.max_retries + 1,
            )
            try:
                async with self.session.get(
                    request_url,
                    headers=self.headers,
                    params=query_params,
                    timeout=self.timeout_duration,
                ) as http_response:
                    response_json: JSONType = await http_response.json()
                    logger.debug(
                        "Success %s -> %s", request_url, response_json
                    )
                    return response_json

            except aiohttp.ClientResponseError as error:
                status_code: int = error.status
                error_message: str = error.message
                logger.warning(
                    "ClientResponseError %s (status=%s), retrying...",
                    request_url,
                    status_code,
                )
                # 5xx => retryable
                if 500 <= status_code < 600:
                    if attempt_count < self.max_retries:
                        sleep_duration = min(
                            self.base_backoff * (2**attempt_count)
                            + random.uniform(0, 0.1 * (2**attempt_count)),
                            self.max_backoff,
                        )
                        await asyncio.sleep(sleep_duration)
                        attempt_count += 1
                    else:
                        raise APIError(
                            status_code,
                            f"Server error after {self.max_retries} retries: "
                            f"{error_message}",
                        )
                else:
                    # 4xx => fail fast
                    raise APIError(status_code, f"Client error: {error_message}")

            except (
                aiohttp.ServerTimeoutError,
                aiohttp.ClientConnectionError,
            ) as network_error:
                network_error_str: str = str(network_error)
                logger.warning(
                    "Network error on %s: %s, retrying...",
                    request_url,
                    network_error_str,
                )
                if attempt_count < self.max_retries:
                    sleep_duration = min(
                        self.base_backoff * (2**attempt_count)
                        + random.uniform(0, 0.1 * (2**attempt_count)),
                        self.max_backoff,
                    )
                    await asyncio.sleep(sleep_duration)
                    attempt_count += 1
                else:
                    raise APIError(
                        None,
                        f"Network failure after {self.max_retries} retries: "
                        f"{network_error_str}",
                    )

        # Should never reach here
        raise APIError(None, "Exceeded retry loop unexpectedly")

    # ──────── Endpoint Methods ─────────────────────────────────────────────────

    async def get_package(
        self, system_name: str, package_name: str
    ) -> JSONType:
        """Fetch basic info about a package, including available versions."""
        logger.info(
            "get_package(system=%s, package_name=%s)",
            system_name,
            package_name,
        )
        validate_system(system_name)
        encoded_name = encode_url_param(package_name)
        endpoint_url = f"{BASE_URL}/systems/{system_name}/packages/{encoded_name}"
        return await self.fetch_data(endpoint_url)

    async def get_version(
        self, system_name: str, package_name: str, version: str
    ) -> JSONType:
        """Fetch detailed info about a specific package version."""
        logger.info(
            "get_version(system=%s, package=%s, version=%s)",
            system_name,
            package_name,
            version,
        )
        validate_system(system_name)
        encoded_name = encode_url_param(package_name)
        encoded_version = encode_url_param(version)
        endpoint_url = (
            f"{BASE_URL}/systems/{system_name}/packages/{encoded_name}"
            f"/versions/{encoded_version}"
        )
        return await self.fetch_data(endpoint_url)

    async def get_version_batch(
        self, system_name: str, package_name: str, version: str
    ) -> JSONType:
        """
        Alias for get_version — provided for batch‐style compatibility.
        """
        return await self.get_version(system_name, package_name, version)

    async def get_requirements(
        self, system_name: str, package_name: str, version: str
    ) -> JSONType:
        """Fetch the declared requirements for a NuGet package version."""
        logger.info(
            "get_requirements(system=%s, package=%s, version=%s)",
            system_name,
            package_name,
            version,
        )
        if system_name.upper() != "NUGET":
            raise ValueError("get_requirements is only available for NuGet.")
        encoded_name = encode_url_param(package_name)
        encoded_version = encode_url_param(version)
        endpoint_url = (
            f"{BASE_URL}/systems/{system_name}/packages/{encoded_name}"
            f"/versions/{encoded_version}:requirements"
        )
        return await self.fetch_data(endpoint_url)

    async def get_dependencies(
        self, system_name: str, package_name: str, version: str
    ) -> JSONType:
        """Fetch the resolved dependency graph for a package version."""
        logger.info(
            "get_dependencies(system=%s, package=%s, version=%s)",
            system_name,
            package_name,
            version,
        )
        validate_system(system_name)
        encoded_name = encode_url_param(package_name)
        encoded_version = encode_url_param(version)
        endpoint_url = (
            f"{BASE_URL}/systems/{system_name}/packages/{encoded_name}"
            f"/versions/{encoded_version}:dependencies"
        )
        return await self.fetch_data(endpoint_url)

    async def get_project(self, project_id: str) -> JSONType:
        """Fetch metadata about a GitHub/GitLab/Bitbucket project."""
        logger.info("get_project(project_id=%s)", project_id)
        encoded_id = encode_url_param(project_id)
        endpoint_url = f"{BASE_URL}/projects/{encoded_id}"
        return await self.fetch_data(endpoint_url)

    async def get_project_package_versions(
        self, project_id: str
    ) -> JSONType:
        """Fetch package versions derived from a source‐control project."""
        logger.info("get_project_package_versions(project_id=%s)", project_id)
        encoded_id = encode_url_param(project_id)
        endpoint_url = f"{BASE_URL}/projects/{encoded_id}:packageversions"
        return await self.fetch_data(endpoint_url)

    async def get_advisory(self, advisory_id: str) -> JSONType:
        """Fetch a security advisory by OSV ID."""
        logger.info("get_advisory(advisory_id=%s)", advisory_id)
        encoded_id = encode_url_param(advisory_id)
        endpoint_url = f"{BASE_URL}/advisories/{encoded_id}"
        return await self.fetch_data(endpoint_url)

    async def query_package_versions(
        self,
        hash_type: Optional[str] = None,
        hash_value: Optional[str] = None,
        version_system: Optional[str] = None,
        version_name: Optional[str] = None,
        version: Optional[str] = None,
    ) -> JSONType:
        """
        Query package versions by content hash or version key fields.
        """
        logger.info(
            "query_package_versions(hash_type=%s, hash_value=%s, "
            "version_system=%s, version_name=%s, version=%s)",
            hash_type,
            hash_value,
            version_system,
            version_name,
            version,
        )
        if hash_type:
            validate_hash(hash_type)
        if version_system:
            validate_system(version_system)

        query_parameters: Dict[str, str] = {}
        if hash_type and hash_value:
            query_parameters["hash.type"] = hash_type
            query_parameters["hash.value"] = hash_value
        if version_system:
            query_parameters["versionKey.system"] = version_system
        if version_name:
            query_parameters["versionKey.name"] = version_name
        if version:
            query_parameters["versionKey.version"] = version

        endpoint_url = f"{BASE_URL}/query"
        return await self.fetch_data(endpoint_url, query_parameters)
