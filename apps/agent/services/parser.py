"""This module defines the ParserService class."""

import logging
import pathlib

from apps.agent.models import models
from apps.agent.services import base_llm


class ParserService(base_llm.BaseLLMService):
    """This class is responsible for prompting the parsing LLM."""

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

    def parse_grocery_text(self, grocery_text: str) -> models.ParsedGroceryList:
        """Parse grocery list submitted by the user."""
        self.logger.debug(f"Parsing grocery text {grocery_text=}")
        resp = None
        try:
            base_prompt = self.base_prompt_file.read_text()
            prompt = [
                {
                    "role": "system",
                    "content": base_prompt,
                },
                {"role": "user", "content": grocery_text},
            ]
            resp = self.client.request_structured_response(
                prompt, models.ParsedGroceryList
            )
            self.logger.debug("Successfully parsed grocery text!")
        except Exception as e:
            self.logger.exception(f"Exception while parsing grocery text: {e}")
        return resp
