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
