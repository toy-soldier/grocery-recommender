"""This module defines the InventoryService class."""

import logging

import tenacity

from apps.agent.clients import api_client
from apps.agent.dependencies import constants, exceptions
from apps.agent.models import models


class InventoryService:
    """This class is responsible for interacting with the API server."""

    def __init__(self, logger: logging.Logger) -> None:
        self.catalog = []
        child_logger = logger.getChild("InventoryService")
        self.logger = child_logger
        self.client = api_client.APIClient(self.logger)
        self.logger.debug("Finished initializing inventory service!")

    def load_catalog(self, products_per_page: int = 50) -> None:
        """Load the store catalog, i.e. product descriptions and SKUs only."""
        self.logger.debug(f"Loading store catalog, {products_per_page=}...")
        list_of_products = []
        try:
            page_to_load = 1
            while page_to_load != -1:
                response = self.client.get_product_listing(
                    page_to_load, products_per_page
                )
                list_of_products.extend(response["data"])
                page_to_load = page_to_load + 1 if response["next"] else -1
            self.logger.debug("Successfully loaded store catalog!")
        except Exception as e:
            list_of_products = []
            self.logger.exception(f"Caught exception while loading store catalog: {e}")
            self.logger.warning("Setting catalog to [].")
        self.catalog = list_of_products

    def get_product(self, product_id: int) -> dict[str, dict[str, str | int | float]]:
        """Get product details."""
        self.logger.debug(f"Getting product with {product_id=}...")
        resp = constants.EMPTY_PRODUCT_DETAILS
        try:
            resp = self.client.get_product_details(product_id)
            self.logger.debug(f"Successfully got product details! {resp=}")
        except tenacity.RetryError as e:
            original_exc = e.last_attempt.exception()
            self.logger.exception(f"Failed after retries due to: {original_exc}")
        except exceptions.ProductNotFoundException:
            self.logger.warning(f"Product {product_id} not found!")
        return resp

    def get_final_recommendations(
        self, recommendations: models.LLMRecommendationList
    ) -> models.AgentRecommendationList:
        """Return the finalized recommendations based on the LLM's recommendations."""
        self.logger.debug("Getting final recommendations...")
        resp = {"recommendations": []}
        self.logger.debug("Final recommendations generated!")
        return resp
