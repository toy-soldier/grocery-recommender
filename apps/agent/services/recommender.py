"""This module defines the RecommenderService class."""

import logging
import pathlib

from apps.agent.models import models
from apps.agent.services import base_llm


class RecommenderService(base_llm.BaseLLMService):
    """This class is responsible for prompting the recommending LLM."""

    def __init__(
        self,
        api_key: str | None,
        model_name: str,
        base_prompt_file: pathlib.Path,
        dummy_responses_folder: pathlib.Path,
        logger: logging.Logger,
    ) -> None:
        super().__init__(
            api_key, model_name, base_prompt_file, dummy_responses_folder, logger
        )

    def recommend_products(
        self, pruned_catalog_list: models.PrunedCatalogList
    ) -> models.LLMRecommendationList:
        """Recommend products based on pruned catalog list."""
        raise NotImplementedError
