# PyDepsDev

A Python library for interacting with the Deps.dev API. Easily fetch package, version, and project data from the API.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
  - [Initialization](#initialization)
  - [Fetching Data](#fetching-data)
- [Contributing](#contributing)
- [License](#license)

## Installation

To install `pydepsdev`, simply run:

```bash
pip3 install pydepsdev
```

## Usage

### Initialization

Start by importing the library and initializing the main class:

```python
from pydepsdev import DepsdevAPI

api = DepsdevAPI()
```

### Fetching Data

The library provides methods that correspond to different endpoints in the Deps.dev API. Here's a breakdown of each method and how to use them:

1. **Get Package Information**

   Fetch package details including available versions.

   ```python
   package_info = await api.get_package("system_name", "package_name")
   ```

2. **Get Version Information**

   Fetch detailed information about a specific package version.

   ```python
   version_info = await api.get_version("system_name", "package_name", "version_number")
   ```

3. **Get Requirements**

   Return the requirements for a specific package version. (Note: Only available for NuGet.)

   ```python
   requirements = await api.get_requirements("NuGet", "package_name", "version_number")
   ```

4. **Get Dependencies**

   Fetch the resolved dependency graph for a specific package version.

   ```python
   dependencies = await api.get_dependencies("system_name", "package_name", "version_number")
   ```

5. **Get Project Information**

   Retrieve details about projects hosted by platforms like GitHub, GitLab, or BitBucket.

   ```python
   project_info = await api.get_project("project_id")
   ```

6. **Get Project Package Versions**

   Fetch the package versions created from a specified source code repository.

   ```python
   project_package_versions = await api.get_project_package_versions("project_id")
   ```

7. **Get Advisory Details**

   Fetch information about a security advisory from OSV.

   ```python
   advisory_info = await api.get_advisory("advisory_id")
   ```

8. **Query Package Versions**

   Query package versions based on content hash or version key.

   ```python
   package_versions = await api.query_package_versions(hash_type="type", hash_value="value", version_system="system_name", version_name="name", version="version_number")
   ```

Get more informating about the query parameters and response values on the [official API documentation](https://docs.deps.dev/api/v3alpha)

## Contributing

We welcome contributions! If you find a bug or have suggestions, feel free to open an issue or submit a pull request.

## License

This project is licensed under the Apache Software License 2.0.
