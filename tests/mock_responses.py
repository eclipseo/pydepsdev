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

GET_PACKAGE_RESPONSE = {
    "packageKey": {"system": "NPM", "name": "@colors/colors"},
    "versions": [
        {
            "versionKey": {
                "system": "NPM",
                "name": "@colors/colors",
                "version": "1.4.0",
            },
            "isDefault": False,
            "publishedAt": "2022-02-12T06:40:43Z",
        },
        {
            "versionKey": {
                "system": "NPM",
                "name": "@colors/colors",
                "version": "1.5.0",
            },
            "isDefault": False,
            "publishedAt": "2022-02-12T07:39:04Z",
        },
        {
            "versionKey": {
                "system": "NPM",
                "name": "@colors/colors",
                "version": "1.6.0",
            },
            "isDefault": True,
            "publishedAt": "2023-07-10T05:16:15Z",
        },
    ],
}

GET_VERSION_RESPONSE = {
    "versionKey": {"system": "NPM", "name": "@colors/colors", "version": "1.4.0"},
    "isDefault": False,
    "licenses": ["MIT"],
    "advisoryKeys": [],
    "links": [
        {"label": "HOMEPAGE", "url": "https://github.com/DABH/colors.js"},
        {
            "label": "ISSUE_TRACKER",
            "url": "https://github.com/DABH/colors.js/issues",
        },
        {
            "label": "ORIGIN",
            "url": "https://registry.npmjs.org/@colors%2Fcolors/1.4.0",
        },
        {
            "label": "SOURCE_REPO",
            "url": "git+ssh://git@github.com/DABH/colors.js.git",
        },
    ],
    "slsaProvenances": [],
    "publishedAt": "2022-02-12T06:40:43Z",
}

GET_REQUIREMENTS_RESPONSE = {
    "nuget": {
        "dependencyGroups": [
            {"targetFramework": ".NETFramework4.6.2", "dependencies": []},
            {
                "targetFramework": ".NETStandard2.0",
                "dependencies": [
                    {"name": "system.diagnostics.eventlog", "requirement": "4.7.0"},
                    {"name": "system.reflection.emit", "requirement": "4.7.0"},
                ],
            },
            {
                "targetFramework": ".NETStandard2.1",
                "dependencies": [
                    {"name": "system.diagnostics.eventlog", "requirement": "4.7.0"}
                ],
            },
            {
                "targetFramework": "net6.0",
                "dependencies": [
                    {"name": "system.diagnostics.eventlog", "requirement": "6.0.0"}
                ],
            },
        ]
    }
}

GET_DEPENDENCIES_RESPONSE = {
    "nodes": [
        {
            "versionKey": {
                "system": "NPM",
                "name": "@colors/colors",
                "version": "1.4.0",
            },
            "bundled": False,
            "relation": "SELF",
            "errors": [],
        }
    ],
    "edges": [],
    "error": "",
}

GET_PROJECT_RESPONSE = {
    "projectKey": {"id": "github.com/pnuckowski/aioresponses"},
    "openIssuesCount": "51",
    "starsCount": "444",
    "forksCount": "83",
    "license": "MIT",
    "description": "Aioresponses is a helper for mock/fake web requests in python aiohttp package.",
    "homepage": "",
    "scorecard": {
        "repository": {
            "name": "github.com/pnuckowski/aioresponses",
            "commit": "56b843319d5d0ae8a405f188e68d7ba8c7573bc8",
        },
        "scorecard": {
            "version": "v4.11.0-79-gf8285ffa",
            "commit": "f8285ffa88e0d8a694816965823e3c021eb8c0bb",
        },
        "checks": [
            {
                "name": "Maintained",
                "documentation": {
                    "shortDescription": 'Determines if the project is "actively maintained".',
                    "url": "https://github.com/ossf/scorecard/blob/f8285ffa88e0d8a694816965823e3c021eb8c0bb/docs/checks.md#maintained",
                },
                "score": "0",
                "reason": "1 commit(s) out of 30 and 0 issue activity out of 30 found in the last 90 days -- score normalized to 0",
                "details": [],
            },
            {
                "name": "Code-Review",
                "documentation": {
                    "shortDescription": "Determines if the project requires human code review before pull requests (aka merge requests) are merged.",
                    "url": "https://github.com/ossf/scorecard/blob/f8285ffa88e0d8a694816965823e3c021eb8c0bb/docs/checks.md#code-review",
                },
                "score": "7",
                "reason": "found 2 unreviewed changesets out of 8 -- score normalized to 7",
                "details": [],
            },
            {
                "name": "CII-Best-Practices",
                "documentation": {
                    "shortDescription": "Determines if the project has an OpenSSF (formerly CII) Best Practices Badge.",
                    "url": "https://github.com/ossf/scorecard/blob/f8285ffa88e0d8a694816965823e3c021eb8c0bb/docs/checks.md#cii-best-practices",
                },
                "score": "0",
                "reason": "no effort to earn an OpenSSF best practices badge detected",
                "details": [],
            },
            {
                "name": "License",
                "documentation": {
                    "shortDescription": "Determines if the project has defined a license.",
                    "url": "https://github.com/ossf/scorecard/blob/f8285ffa88e0d8a694816965823e3c021eb8c0bb/docs/checks.md#license",
                },
                "score": "10",
                "reason": "license file detected",
                "details": [
                    "Info: License file found in expected location: LICENSE:1",
                    "Info: FSF or OSI recognized license: LICENSE:1",
                ],
            },
            {
                "name": "Branch-Protection",
                "documentation": {
                    "shortDescription": "Determines if the default and release branches are protected with GitHub's branch protection settings.",
                    "url": "https://github.com/ossf/scorecard/blob/f8285ffa88e0d8a694816965823e3c021eb8c0bb/docs/checks.md#branch-protection",
                },
                "score": "-1",
                "reason": "internal error: error during branchesHandler.setup: internal error: githubv4.Query: Resource not accessible by integration",
                "details": [],
            },
            {
                "name": "Signed-Releases",
                "documentation": {
                    "shortDescription": "Determines if the project cryptographically signs release artifacts.",
                    "url": "https://github.com/ossf/scorecard/blob/f8285ffa88e0d8a694816965823e3c021eb8c0bb/docs/checks.md#signed-releases",
                },
                "score": "-1",
                "reason": "no releases found",
                "details": ["Warn: no GitHub releases found"],
            },
            {
                "name": "Packaging",
                "documentation": {
                    "shortDescription": "Determines if the project is published as a package that others can easily download, install, easily update, and uninstall.",
                    "url": "https://github.com/ossf/scorecard/blob/f8285ffa88e0d8a694816965823e3c021eb8c0bb/docs/checks.md#packaging",
                },
                "score": "-1",
                "reason": "no published package detected",
                "details": ["Warn: no GitHub/GitLab publishing workflow detected"],
            },
            {
                "name": "Dangerous-Workflow",
                "documentation": {
                    "shortDescription": "Determines if the project's GitHub Action workflows avoid dangerous patterns.",
                    "url": "https://github.com/ossf/scorecard/blob/f8285ffa88e0d8a694816965823e3c021eb8c0bb/docs/checks.md#dangerous-workflow",
                },
                "score": "10",
                "reason": "no dangerous workflow patterns detected",
                "details": [],
            },
            {
                "name": "Token-Permissions",
                "documentation": {
                    "shortDescription": "Determines if the project's workflows follow the principle of least privilege.",
                    "url": "https://github.com/ossf/scorecard/blob/f8285ffa88e0d8a694816965823e3c021eb8c0bb/docs/checks.md#token-permissions",
                },
                "score": "0",
                "reason": "detected GitHub workflow tokens with excessive permissions",
                "details": [
                    "Warn: no topLevel permission defined: .github/workflows/ci.yml:1: Visit https://app.stepsecurity.io/secureworkflow/pnuckowski/aioresponses/ci.yml/master?enable=permissions\nTick the 'Restrict permissions for GITHUB_TOKEN'\nUntick other options\nNOTE: If you want to resolve multiple issues at once, you can visit https://app.stepsecurity.io/securerepo instead. (Low effort)",
                    "Warn: no topLevel permission defined: .github/workflows/flake8.yml:1: Visit https://app.stepsecurity.io/secureworkflow/pnuckowski/aioresponses/flake8.yml/master?enable=permissions\nTick the 'Restrict permissions for GITHUB_TOKEN'\nUntick other options\nNOTE: If you want to resolve multiple issues at once, you can visit https://app.stepsecurity.io/securerepo instead. (Low effort)",
                    "Info: no jobLevel write permissions found",
                ],
            },
            {
                "name": "Binary-Artifacts",
                "documentation": {
                    "shortDescription": "Determines if the project has generated executable (binary) artifacts in the source repository.",
                    "url": "https://github.com/ossf/scorecard/blob/f8285ffa88e0d8a694816965823e3c021eb8c0bb/docs/checks.md#binary-artifacts",
                },
                "score": "10",
                "reason": "no binaries found in the repo",
                "details": [],
            },
            {
                "name": "Pinned-Dependencies",
                "documentation": {
                    "shortDescription": "Determines if the project has declared and pinned the dependencies of its build process.",
                    "url": "https://github.com/ossf/scorecard/blob/f8285ffa88e0d8a694816965823e3c021eb8c0bb/docs/checks.md#pinned-dependencies",
                },
                "score": "6",
                "reason": "dependency not pinned by hash detected -- score normalized to 6",
                "details": [
                    "Warn: GitHub-owned GitHubAction not pinned by hash: .github/workflows/ci.yml:88: update your workflow using https://app.stepsecurity.io/secureworkflow/pnuckowski/aioresponses/ci.yml/master?enable=pin",
                    "Warn: GitHub-owned GitHubAction not pinned by hash: .github/workflows/ci.yml:90: update your workflow using https://app.stepsecurity.io/secureworkflow/pnuckowski/aioresponses/ci.yml/master?enable=pin",
                    "Warn: third-party GitHubAction not pinned by hash: .github/workflows/ci.yml:100: update your workflow using https://app.stepsecurity.io/secureworkflow/pnuckowski/aioresponses/ci.yml/master?enable=pin",
                    "Warn: GitHub-owned GitHubAction not pinned by hash: .github/workflows/flake8.yml:15: update your workflow using https://app.stepsecurity.io/secureworkflow/pnuckowski/aioresponses/flake8.yml/master?enable=pin",
                    "Warn: GitHub-owned GitHubAction not pinned by hash: .github/workflows/flake8.yml:17: update your workflow using https://app.stepsecurity.io/secureworkflow/pnuckowski/aioresponses/flake8.yml/master?enable=pin",
                    "Warn: third-party GitHubAction not pinned by hash: .github/workflows/flake8.yml:21: update your workflow using https://app.stepsecurity.io/secureworkflow/pnuckowski/aioresponses/flake8.yml/master?enable=pin",
                    "Warn: pipCommand not pinned by hash: .github/workflows/ci.yml:95",
                    "Warn: pipCommand not pinned by hash: .github/workflows/ci.yml:96",
                    "Info: Dockerfile dependencies are pinned",
                    "Info: no insecure (not pinned by hash) dependency downloads found in Dockerfiles",
                    "Info: no insecure (not pinned by hash) dependency downloads found in shell scripts",
                    "Info: npm installs are pinned",
                ],
            },
            {
                "name": "Fuzzing",
                "documentation": {
                    "shortDescription": "Determines if the project uses fuzzing.",
                    "url": "https://github.com/ossf/scorecard/blob/f8285ffa88e0d8a694816965823e3c021eb8c0bb/docs/checks.md#fuzzing",
                },
                "score": "0",
                "reason": "project is not fuzzed",
                "details": [],
            },
            {
                "name": "Security-Policy",
                "documentation": {
                    "shortDescription": "Determines if the project has published a security policy.",
                    "url": "https://github.com/ossf/scorecard/blob/f8285ffa88e0d8a694816965823e3c021eb8c0bb/docs/checks.md#security-policy",
                },
                "score": "0",
                "reason": "security policy file not detected",
                "details": [],
            },
            {
                "name": "Vulnerabilities",
                "documentation": {
                    "shortDescription": "Determines if the project has open, known unfixed vulnerabilities.",
                    "url": "https://github.com/ossf/scorecard/blob/f8285ffa88e0d8a694816965823e3c021eb8c0bb/docs/checks.md#vulnerabilities",
                },
                "score": "10",
                "reason": "no vulnerabilities detected",
                "details": [],
            },
            {
                "name": "SAST",
                "documentation": {
                    "shortDescription": "Determines if the project uses static code analysis.",
                    "url": "https://github.com/ossf/scorecard/blob/f8285ffa88e0d8a694816965823e3c021eb8c0bb/docs/checks.md#sast",
                },
                "score": "0",
                "reason": "SAST tool is not run on all commits -- score normalized to 0",
                "details": [
                    "Warn: 0 commits out of 30 are checked with a SAST tool",
                    "Warn: CodeQL tool not detected",
                ],
            },
        ],
        "overallScore": 4.9,
        "metadata": [],
        "date": "2023-07-31T00:00:00Z",
    },
}

GET_ADVISORY_RESPONSE = {
    "advisoryKey": {"id": "GHSA-2qrg-x229-3v8q"},
    "url": "https://osv.dev/vulnerability/GHSA-2qrg-x229-3v8q",
    "title": "Deserialization of Untrusted Data in Log4j",
    "aliases": ["CVE-2019-17571"],
    "cvss3Score": 9.8,
    "cvss3Vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
}


GET_QUERY_RESPONSE = {
    "results": [
        {
            "version": {
                "versionKey": {"system": "NPM", "name": "react", "version": "18.2.0"},
                "purl": "pkg:npm/react@18.2.0",
                "publishedAt": "2022-06-14T19:46:38Z",
                "isDefault": False,
                "isDeprecated": False,
                "licenses": ["MIT"],
                "licenseDetails": [{"license": "MIT", "spdx": "MIT"}],
                "advisoryKeys": [],
                "links": [
                    {"label": "HOMEPAGE", "url": "https://reactjs.org/"},
                    {
                        "label": "ISSUE_TRACKER",
                        "url": "https://github.com/facebook/react/issues",
                    },
                    {
                        "label": "ORIGIN",
                        "url": "https://registry.npmjs.org/react/18.2.0",
                    },
                    {
                        "label": "SOURCE_REPO",
                        "url": "git+https://github.com/facebook/react.git",
                    },
                ],
                "slsaProvenances": [],
                "attestations": [],
                "registries": ["https://registry.npmjs.org/"],
                "relatedProjects": [
                    {
                        "projectKey": {"id": "github.com/facebook/react"},
                        "relationProvenance": "UNVERIFIED_METADATA",
                        "relationType": "ISSUE_TRACKER",
                    },
                    {
                        "projectKey": {"id": "github.com/facebook/react"},
                        "relationProvenance": "UNVERIFIED_METADATA",
                        "relationType": "SOURCE_REPO",
                    },
                ],
                "upstreamIdentifiers": [],
            },
            "artifacts": [],
        }
    ]
}
