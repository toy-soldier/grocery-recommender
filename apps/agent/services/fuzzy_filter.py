"""This module defines the FuzzyFilterService class."""

import logging

from rapidfuzz import process

from apps.agent.models import models


class FuzzyFilterService:
    """This class is responsible for running fuzzy matching on the store catalog."""

    def __init__(self, top_n: int, min_score: int, logger: logging.Logger) -> None:
        child_logger = logger.getChild("FuzzyFilterService")
        self.logger = child_logger
        self.top_n = top_n
        self.min_score = min_score
        self.logger.debug(
            f"Finished initializing fuzzy matching service, {self.top_n=} and {self.min_score=}!"
        )

    def filter_catalog(
        self, data: models.CatalogForFuzzyMatching
    ) -> models.PrunedCatalog:
        """Returns a pruned catalog with only the top N matches per grocery item."""
        pruned_catalog = {}

        store_catalog = data.catalog.catalog
        grocery_list = data.grocery_list.grocery_list
        self.logger.debug(f"Got {grocery_list=}, now pruning store catalog...")
        products = {item.sku: item.description for item in store_catalog}

        # For each item in the parsed grocery list, find top matches
        # extract() uses fuzz.WRatio by default
        for line_item in grocery_list:
            matches = process.extract(
                query=line_item.product,
                choices=products,
                limit=self.top_n,
                score_cutoff=self.min_score,
            )

            # matches is a list of (product_description, score, sku)
            for match_name, score, key in matches:
                pruned_catalog[key] = match_name

        self.logger.debug(f"Got {pruned_catalog=}")
        final_product_list = [
            models.ProductLineItem(sku=k, description=v)
            for k, v in pruned_catalog.items()
        ]
        return models.PrunedCatalog(catalog=final_product_list)
