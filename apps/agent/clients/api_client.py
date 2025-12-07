"""This module defines the APIClient class."""

import logging

import requests
import tenacity

from apps.agent.dependencies import constants as c, exceptions as exc


class APIClient:
    """This class acts as a wrapper for the "requests" library."""

    def __init__(self, logger: logging.Logger) -> None:
        child_logger = logger.getChild("APIClient")
        self.logger = child_logger
        self.logger.debug("Finished initializing APIClient!")

    @tenacity.retry(
        retry=tenacity.retry_if_not_exception_type(exc.ProductNotFoundException),
        stop=tenacity.stop_after_attempt(c.GROCERY_API_SERVER_RETRIES),
        wait=tenacity.wait_exponential(
            multiplier=c.GROCERY_API_SERVER_BACKOFF_EXPONENTIAL_FACTOR,
            min=c.GROCERY_API_SERVER_BACKOFF_MINIMUM,
            max=c.GROCERY_API_SERVER_BACKOFF_MAXIMUM,
        ),
    )
    def get_product_details(
        self, product_id: int
    ) -> dict[str, str | int | float] | None:
        """Return a product's details."""
        self.logger.debug(f"Getting details of {product_id=}...")
        url = c.GROCERY_API_SERVER_BASE_URL + c.GROCERY_API_SERVER_GET_PRODUCT.format(
            product_id
        )
        try:
            response = requests.get(url)
            if response.status_code == requests.codes.ok:
                self.logger.debug(f"Successfully retrieved {product_id=}!")
                return response.json()
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            status_code = err.response.status_code
            if status_code == requests.codes.not_found:
                raise exc.ProductNotFoundException()
            raise exc.APIServerException(status_code)
        except Exception as e:
            self.logger.exception(f"A different error has occurred: {e}")
            raise exc.APIServerException(500)

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(c.GROCERY_API_SERVER_RETRIES),
        wait=tenacity.wait_exponential(
            multiplier=c.GROCERY_API_SERVER_BACKOFF_EXPONENTIAL_FACTOR,
            min=c.GROCERY_API_SERVER_BACKOFF_MINIMUM,
            max=c.GROCERY_API_SERVER_BACKOFF_MAXIMUM,
        ),
    )
    def get_product_listing(
        self, page: int, products_per_page: int
    ) -> dict[str, int | str | list[dict[str, str | int]]] | None:
        """Return a page of the store catalog."""
        self.logger.debug(f"Getting {page=} and {products_per_page=}...")
        url = c.GROCERY_API_SERVER_BASE_URL + c.GROCERY_API_SERVER_GET_LISTING
        params = {"page": page, "products_per_page": products_per_page}
        try:
            response = requests.get(url, params=params)
            if response.status_code == requests.codes.ok:
                self.logger.debug("Successfully retrieved listing!")
                return response.json()
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise exc.APIServerException(err.response.status_code)
        except Exception as e:
            self.logger.exception(f"A different error has occurred: {e}")
            raise exc.APIServerException(500)
