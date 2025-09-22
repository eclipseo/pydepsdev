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

BASE_URL = "https://api.deps.dev/v3alpha"
SUPPORTED_SYSTEMS = ["GO", "RUBYGEMS", "NPM", "CARGO", "MAVEN", "PYPI", "NUGET"]
SUPPORTED_SYSTEMS_REQUIREMENTS = ["RUBYGEMS", "NPM", "MAVEN", "NUGET"]
SUPPORTED_SYSTEMS_DEPENDENCIES = ["NPM", "CARGO", "MAVEN", "PYPI"]
SUPPORTED_SYSTEMS_DEPENDENTS = ["NPM", "CARGO", "MAVEN", "PYPI"]
SUPPORTED_SYSTEMS_CAPABILITIES = ["GO"]
SUPPORTED_SYSTEMS_QUERY = ["RUBYGEMS", "NPM", "CARGO", "MAVEN", "PYPI", "NUGET"]
SUPPORTED_HASHES = ["MD5", "SHA1", "SHA256", "SHA512"]

DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_BACKOFF = 1
DEFAULT_MAX_BACKOFF = 5
DEFAULT_TIMEOUT_DURATION = 20
