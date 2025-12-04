"""This module defines the ParserService class."""

import logging
import pathlib

from apps.agent.services import base_llm
from apps.agent import constants


class ParserService(base_llm.BaseLLMService):
    """This class is responsible for prompting the parsing LLM."""

    def __init__(self, api_key: str | None, prompt_file: pathlib.Path, logger: logging.Logger) -> None:
        super().__init__(api_key, prompt_file, constants.PARSER_LLM_MODEL, logger)
