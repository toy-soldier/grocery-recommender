"""This module defines the BaseLLMService class."""

import json
import logging
import pathlib

from apps.agent.models import models
from apps.agent.clients import openai_client


class BaseLLMService:
    """This class is responsible for prompting the LLM."""

    def __init__(
        self,
        api_key: str | None,
        model_name: str,
        base_prompt_file: pathlib.Path,
        dummy_responses_folder: pathlib.Path,
        logger: logging.Logger,
    ) -> None:
        self.api_key = api_key
        self.base_prompt_file = base_prompt_file
        self.dummy_responses_folder = dummy_responses_folder
        class_name = self.__class__.__name__
        child_logger = logger.getChild(class_name)
        self.logger = child_logger
        self.client = (
            openai_client.OpenAIClient(self.api_key, model_name, self.logger)
            if self.api_key
            else None
        )
        self.logger.debug(
            f"Finished initializing {class_name} with {self. base_prompt_file=}!"
        )

    def return_mocked_response(
        self, filename: str
    ) -> models.ParsedGroceryList | models.LLMRecommendationList | None:
        """Return a mocked response based on the grocery list's filename."""
        class_ = self.__class__.__name__
        model = (
            models.ParsedGroceryList
            if class_ == "ParserService"
            else models.LLMRecommendationList
        )
        resp = None
        self.logger.debug(f"Returning mocked response for {filename} from {class_}...")
        try:
            content = json.load(
                open(self.dummy_responses_folder / filename, mode="r", encoding="utf-8")
            )
            resp = model.model_validate(content)
            self.logger.debug("Successfully retrieved mocked response for {filename}!")
        except Exception as e:
            self.logger.exception(f"Exception while retrieving mocked response: {e}")
        return resp
