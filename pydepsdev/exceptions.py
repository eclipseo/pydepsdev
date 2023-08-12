class APIError(Exception):
    """
    Raised when an API call encounters an error.

    Attributes:
        status (int): HTTP status code of the error. None if not available.
        message (str): Explanation of the error.
    """

    def __init__(self, status, message):
        self.status = status
        self.message = message
        super().__init__(self.message)
