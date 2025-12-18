"""This module defines the OpenAIClient class."""

import logging
from typing import Callable

import openai
import pydantic
import tenacity
from openai.types.responses import Response

from apps.agent.dependencies import constants as c

retryable_exceptions = (
    openai.RateLimitError,
    openai.APIConnectionError,
    openai.InternalServerError,
)


class OpenAIClient:
    """This class acts as a wrapper for the openai client."""

    def __init__(self, api_key: str, model: str, logger: logging.Logger) -> None:
        child_logger = logger.getChild("OpenAIClient")
        self.logger = child_logger
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)
        self.logger.debug(f"Finished initializing OpenAIClient with {self.model=}!")

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(retryable_exceptions),
        stop=tenacity.stop_after_attempt(c.OPENAI_PLATFORM_RETRIES),
        wait=tenacity.wait_exponential(
            multiplier=c.OPENAI_PLATFORM_BACKOFF_EXPONENTIAL_FACTOR,
            min=c.OPENAI_PLATFORM_BACKOFF_MINIMUM,
            max=c.OPENAI_PLATFORM_BACKOFF_MAXIMUM,
        ),
    )
    def _send_request(self, func: Callable, prompt: str, **kwargs) -> Response:
        """
        Send a request to the model and return its response.
        This is used internally by the methods that expect different response formats
        """
        self.logger.debug(f"Sending request to model {self.model=}")
        try:
            response = func(model=self.model, input=prompt, temperature=0, **kwargs)
            self.logger.debug("Got response from model!")
            return response
        except Exception as e:
            self.logger.exception(f"Got exception when requesting from model: {e}")
            raise e

    def request_string_response(self, prompt: str) -> str:
        """Request a string response from the model."""
        self.logger.debug("Requesting string response from model...")
        func = self.client.responses.create
        response = self._send_request(func, prompt)
        self.logger.debug("Successfully received string response!")
        return response.output_text

    def request_json_response(self, prompt: str) -> str:
        """Request a JSON response from the model."""
        self.logger.debug("Requesting JSON response from model...")
        func = self.client.responses.create
        response = self._send_request(
            func, prompt, text={"format": {"type": "json_object"}}
        )
        self.logger.debug("Successfully received JSON response!")
        return response.output_text

    def request_structured_response(
        self, prompt: str, response_model: type[pydantic.BaseModel]
    ) -> pydantic.BaseModel:
        """Request a response in a Pydantic model."""
        self.logger.debug("Requesting structured response from model...")
        func = self.client.responses.parse
        response = self._send_request(func, prompt, text_format=response_model)
        self.logger.debug("Successfully received structured response!")
        return response.output_parsed
