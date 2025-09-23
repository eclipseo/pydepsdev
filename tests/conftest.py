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

import asyncio
import pytest
import pytest_asyncio
from pydepsdev.api import DepsdevAPI


@pytest_asyncio.fixture(autouse=True)
def no_sleep(monkeypatch):
    """
    Stub out asyncio.sleep so that our retry/backoff loops don’t actually wait.
    """

    async def dummy_sleep(*args, **kwargs):
        return None

    monkeypatch.setattr(asyncio, "sleep", dummy_sleep)


@pytest_asyncio.fixture
async def api_client():
    """
    Provides a DepsdevAPI client with zero backoff (fast tests)
    and closes it automatically at teardown.
    """
    client = DepsdevAPI(
        timeout_duration=0.1,
        max_retries=2,
        base_backoff=0,
        max_backoff=0,
    )
    yield client
    await client.close()
