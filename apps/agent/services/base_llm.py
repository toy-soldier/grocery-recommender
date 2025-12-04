"""This module defines the BaseLLMService class."""

import logging
import pathlib

from apps.agent.clients import openai_client


class BaseLLMService:
    """This class is responsible for prompting the LLM."""

    def __init__(self, api_key: str | None, prompt_file: pathlib.Path,
                 model_name: str, logger: logging.Logger) -> None:
        self.api_key = api_key
        self.prompt_file = prompt_file
        class_name = self.__class__.__name__
        child_logger = logger.getChild(class_name)
        self.logger = child_logger
        self.client = openai_client.OpenAIClient(self.api_key, model_name, self.logger) if self.api_key else None
        self.logger.debug(
            f"Finished initializing {class_name} with {self.prompt_file=}!"
        )
