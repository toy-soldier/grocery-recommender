"""This module defines the APIClient class."""
import logging


class APIClient:
    """This class acts as a wrapper for the requests library."""

    def __init__(self, logger: logging.Logger) -> None:
        child_logger = logger.getChild("APIClient")
        self.logger = child_logger
        self.logger.debug("Finished initializing APIClient!")

    def get_product_listing(self, page_number: int, products_per_page: int) -> dict:
        """Return a page of the store catalog."""
        self.logger.debug(f"Getting {page_number=} and {products_per_page=}...")
        return {}

    def get_product_details(self, product_id: int) -> dict:
        """Return a product's details."""
        self.logger.debug(f"Getting details of {product_id=}...")
        return {}
