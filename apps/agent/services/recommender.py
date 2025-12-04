"""This module defines the RecommenderService class."""

import logging
import pathlib

from apps.agent.services import base_llm
from apps.agent import constants


class RecommenderService(base_llm.BaseLLMService):
    """This class is responsible for prompting the recommending LLM."""

    def __init__(self, api_key: str | None, prompt_file: pathlib.Path, logger: logging.Logger) -> None:
        super().__init__(api_key, prompt_file, constants.RECOMMENDER_LLM_MODEL, logger)
