"""This module defines custom exceptions."""


class ServerException(Exception):
    """Exception raised when a server is unable to handle the client request."""

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"Server error with status code {status_code}")


class APIServerException(ServerException):
    """Exception raised when the API server is unable to handle the client request."""

    pass


class ProductNotFoundException(APIServerException):
    """Exception raised when the product is not found."""

    def __init__(self) -> None:
        super().__init__(404)
        self.message = "Product not found"
