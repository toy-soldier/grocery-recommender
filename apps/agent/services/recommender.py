"""This module defines the RecommenderService class."""

import json
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
        self.logger.debug("Generating product recommendations...")
        resp = None
        try:
            dumped_list = json.dumps(pruned_catalog_list.model_dump())
            self.logger.debug(f"Pruned catalog: {dumped_list}")
            base_prompt = self.base_prompt_file.read_text()
            prompt = [
                {
                    "role": "system",
                    "content": base_prompt,
                },
                {"role": "user", "content": dumped_list},
            ]
            resp = self.client.request_structured_response(
                prompt, models.LLMRecommendationList
            )
            self.logger.debug("Successfully generated product recommendations!")
        except Exception as e:
            self.logger.exception(
                f"Exception while generating product recommendations: {e}"
            )
        return resp
