# MOVED TO https://codeberg.org/eclipseo/pydepsdev

# PyDepsDev

A Python library for interacting with Open Source Insights API (deps.dev).  
Easily fetch package, version, project, advisory, container, and PURL data—and leverage automatic name normalization and hash encoding.

## Table of Contents

- [Installation](#installation)  
- [Quick Start](#quick-start)  
- [Name Normalization & Hash Encoding](#name-normalization--hash-encoding)  
- [Endpoints](#endpoints)  
  - [Package & Version](#package--version)  
  - [Batch Version Queries](#batch-version-queries)  
  - [Requirements, Dependencies & Dependents](#requirements-dependencies--dependents)  
  - [Capabilities & Similarly-Named](#capabilities--similarly-named)  
  - [Project](#project)  
  - [Advisories](#advisories)  
  - [PURL Lookup](#purl-lookup)  
  - [Container Images](#container-images)  
- [Contributing](#contributing)  
- [License](#license)  

## Installation

```bash
pip install pydepsdev
```

## Quick Start

```python
import asyncio
from pydepsdev.api import DepsdevAPI

async def main():
    # Simple init
    api = DepsdevAPI()

    # …use api methods…

    await api.close()

asyncio.run(main())
```

Or use as an async context manager:

```python
import asyncio
from pydepsdev.api import DepsdevAPI

async def main():
    async with DepsdevAPI() as api:
        pkg_info = await api.get_package("npm", "foo")
        print(pkg_info)

asyncio.run(main())
```

## Name Normalization & Hash Encoding

- **System names** are case‐insensitive but always sent uppercase.  
- **NuGet** package names are lowercased.  
- **PyPI** package names are normalized per [PEP 503].  
- When you call `query_package_versions(hash_type, hash_value, …)`, your `hash_value` is automatically Base64‐encoded before sending.

## Endpoints

### Package & Version

```python
# Get basic package info + versions list
await api.get_package(system_name: str, package_name: str)

# Get metadata for a specific version
await api.get_version(system_name: str, package_name: str, version: str)
```

### Batch Version Queries

```python
# One page (up to 5000) of versions
await api.get_version_batch(
    [(system, pkg, ver), …],
    page_token: Optional[str] = None
)

# Retrieve ALL pages for a batch
await api.get_all_versions_batch(
    [(system, pkg, ver), …]
)
```

### Requirements, Dependencies & Dependents

```python
# NuGet only
await api.get_requirements("NuGet", "package_name", "version")

# Any supported system
await api.get_dependencies(system_name, package_name, version)

# Dependent counts
await api.get_dependents(system_name, package_name, version)
```

### Capabilities & Similarly-Named

```python
# Go only
await api.get_capabilities("Go", "module_path", "version")

# Find similarly-named packages
await api.get_similarly_named_packages(system_name, package_name)
```

### Query Package Versions

```python
# By hash (hash.value is auto base64‐encoded)
await api.query_package_versions(
    hash_type: str,     # e.g. "SHA256"
    hash_value: str,    # raw hex or bytes
    version_system: Optional[str] = None,
    version_name:   Optional[str] = None,
    version:        Optional[str] = None,
)
```

### Project

```python
# Single project metadata
await api.get_project(project_id: str)

# One page of project batch
await api.get_project_batch(
    [project_id1, project_id2, …],
    page_token: Optional[str] = None
)

# Retrieve all pages
await api.get_all_projects_batch([…])

# List package versions derived from a project
await api.get_project_package_versions(project_id: str)
```

### Advisories

```python
# Fetch OSV advisory details
await api.get_advisory(advisory_id: str)
```

### PURL Lookup

```python
# Single purl
await api.get_purl_lookup(purl: str)

# One page of PURL batch
await api.get_purl_lookup_batch(
    [purl1, purl2, …],
    page_token: Optional[str] = None
)

# Retrieve all pages
await api.get_all_purl_lookup_batch([…])
```

### Container Images

```python
# Query container images by OCI chain ID
await api.query_container_images(chain_id: str)
```

For full details on parameters and response schemas, see the [Deps.dev API docs](https://docs.deps.dev/api/v3alpha).

## Contributing

Contributions, issues and feature requests are welcome!  
Feel free to check [issues page](https://github.com/eclipseo/pydepsdev/issues) or submit a pull request.

## License
This project is licensed under the Apache Software License 2.0.
