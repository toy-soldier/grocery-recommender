"""This module defines the OpenAIClient class."""

import logging

import openai
import tenacity


class OpenAIClient:
    """This class acts as a wrapper for the OpenAI client."""

    def __init__(self, api_key: str, model: str, logger: logging.Logger) -> None:
        child_logger = logger.getChild("OpenAIClient")
        self.logger = child_logger
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)
        self.logger.debug(f"Finished initializing OpenAIClient with {self.model=}!")

    def send_prompt(self, prompt: str) -> str:
        """Send a prompt to the model and return its response."""
        self.logger.debug(f"Sending prompt to model {self.model=}")
        resp = self.client.responses.create(model=self.model, input=prompt)
        return resp.output_text
