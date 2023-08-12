import aiohttp
import asyncio
import logging
import random
from .constants import (
    BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_BASE_BACKOFF,
    DEFAULT_MAX_BACKOFF,
    DEFAULT_TIMEOUT_DURATION,
)
from .exceptions import APIError
from .utils import encode_url_param, validate_system, validate_hash

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DepsdevAPI:
    def __init__(
        self,
        timeout_duration=DEFAULT_TIMEOUT_DURATION,
        max_retries=DEFAULT_MAX_RETRIES,
        base_backoff=DEFAULT_BASE_BACKOFF,
        max_backoff=DEFAULT_MAX_BACKOFF,
    ):
        self.session = aiohttp.ClientSession()
        self.headers = {
            "Content-Type": "application/json",
        }
        self.timeout_duration = timeout_duration
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.max_backoff = max_backoff
        logger.debug(
            "DepsdevAPI initialized with params: %s, %s, %s, %s",
            timeout_duration,
            max_retries,
            base_backoff,
            max_backoff,
        )

    async def close(self):
        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def fetch_data(self, url, params=None):
        retries = 0
        while retries <= self.max_retries:
            logger.info(
                f"Making request to {url} with params {params}. Attempt {retries + 1} of {self.max_retries + 1}"
            )
            try:
                async with self.session.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=self.timeout_duration,
                ) as response:
                    data = await response.json()
                    logger.debug(f"Successful request to {url}. Received data: {data}")
                    return data
            except aiohttp.ClientResponseError as e:
                logger.warning(
                    f"ClientResponseError on {url}. Status: {e.status}. Retrying..."
                )
                if 500 <= e.status < 600:
                    if retries < self.max_retries:
                        backoff = min(
                            self.base_backoff * (2**retries)
                            + random.uniform(0, 0.1 * (2**retries)),
                            self.max_backoff,
                        )
                        await asyncio.sleep(backoff)
                        retries += 1
                    else:
                        # After exhausting the retries
                        raise APIError(
                            e.status,
                            f"Server error: {e.message}. Failed after {self.max_retries} retries",
                        )
                else:
                    # For 4xx errors, we just raise the error without retrying
                    raise APIError(e.status, f"Client error: {e.message}")

            except (aiohttp.ServerTimeoutError, aiohttp.ClientConnectionError) as e:
                logger.warning(f"Error {str(e)} on {url}. Retrying...")
                if retries < self.max_retries:
                    backoff = min(
                        self.base_backoff * (2**retries)
                        + random.uniform(0, 0.1 * (2**retries)),
                        self.max_backoff,
                    )
                    await asyncio.sleep(backoff)
                    retries += 1
                else:
                    raise APIError(
                        None,
                        f"Failed after {self.max_retries} retries due to: {str(e)}",
                    )

    # Endpoint Functions

    async def get_package(self, system, package_name):
        """Return package information including available versions."""
        logger.info(
            f"Fetching package for system: {system} and package_name: {package_name}"
        )
        validate_system(system)
        encoded_package_name = encode_url_param(package_name)
        url = f"{BASE_URL}/systems/{system}/packages/{encoded_package_name}"
        return await self.fetch_data(url)

    async def get_version(self, system, package_name, version):
        """Return detailed information about a specific package version."""
        logger.info(
            f"Fetching version data for system: {system}, package_name: {package_name}, version: {version}"
        )
        validate_system(system)
        encoded_package_name = encode_url_param(package_name)
        encoded_version = encode_url_param(version)
        url = f"{BASE_URL}/systems/{system}/packages/{encoded_package_name}/versions/{encoded_version}"
        return await self.fetch_data(url)

    async def get_requirements(self, system, package_name, version):
        """Return the requirements for a specific package version."""
        logger.info(
            f"Fetching requirements for system: {system}, package_name: {package_name}, version: {version}"
        )
        if system.upper() != "NUGET":
            raise ValueError("GetRequirements is currently only available for NuGet.")

        encoded_package_name = encode_url_param(package_name)
        encoded_version = encode_url_param(version)
        url = f"{BASE_URL}/systems/{system}/packages/{encoded_package_name}/versions/{encoded_version}:requirements"
        return await self.fetch_data(url)

    async def get_dependencies(self, system, package_name, version):
        """Return the resolved dependency graph for a specific package version."""
        logger.info(
            f"Fetching dependencies for system: {system}, package_name: {package_name}, version: {version}"
        )
        validate_system(system)
        encoded_package_name = encode_url_param(package_name)
        encoded_version = encode_url_param(version)
        url = f"{BASE_URL}/systems/{system}/packages/{encoded_package_name}/versions/{encoded_version}:dependencies"
        return await self.fetch_data(url)

    async def get_project(self, project_id):
        """Return information about projects hosted by GitHub, GitLab, or BitBucket."""
        logger.info(f"Fetching project with ID: {project_id}")
        encoded_project_id = encode_url_param(project_id)
        url = f"{BASE_URL}/projects/{encoded_project_id}"
        return await self.fetch_data(url)

    async def get_project_package_versions(self, project_id):
        """Return the package versions created from the specified source code repository."""
        logger.info(f"Fetching package versions for project ID: {project_id}")
        encoded_project_id = encode_url_param(project_id)
        url = f"{BASE_URL}/projects/{encoded_project_id}:packageversions"
        return await self.fetch_data(url)

    async def get_advisory(self, advisory_id):
        """Return information about a security advisory from OSV."""
        logger.info(f"Fetching advisory with ID: {advisory_id}")
        encoded_advisory_id = encode_url_param(advisory_id)
        url = f"{BASE_URL}/advisories/{encoded_advisory_id}"
        return await self.fetch_data(url)

    async def query_package_versions(
        self,
        hash_type=None,
        hash_value=None,
        version_system=None,
        version_name=None,
        version=None,
    ):
        """Query package versions based on content hash or version key."""
        logger.info(
            f"Querying package versions with hash_type: {hash_type}, hash_value: {hash_value}, version_system: {version_system}, version_name: {version_name}, version: {version}"
        )
        if hash_type:
            validate_hash(hash_type)
        if version_system:
            validate_system(version_system)
        # Construct URL with appropriate query parameters
        query_params = {}
        if hash_type and hash_value:
            query_params["hash.type"] = hash_type
            query_params["hash.value"] = hash_value
        if version_system:
            query_params["versionKey.system"] = version_system
        if version_name:
            query_params["versionKey.name"] = version_name
        if version:
            query_params["versionKey.version"] = version

        url = f"{BASE_URL}/query"
        return await self.fetch_data(url, params=query_params)
