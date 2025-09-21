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

from typing import Optional


class APIError(Exception):
    """
    Raised when an API call encounters an error.

    Attributes:
        status (Optional[int]): HTTP status code of the error, if available.
        message (str): Explanation of the error.
    """

    status: Optional[int]
    message: str

    def __init__(self, status: Optional[int], message: str) -> None:
        """
        Initialize a new APIError.

        Args:
            status (Optional[int]): HTTP status code returned by the API,
                or None if the status is not available (e.g., network error).
            message (str): Human-readable description of the error.
        """
        self.status = status
        self.message = message
        super().__init__(self.message)
