"""This module contains all orchestration logic."""

import logging
import os
import pathlib
from typing import Any

from dotenv import load_dotenv

from apps.agent.dependencies import constants
from apps.agent.models import models
from apps.agent.services import (
    fuzzy_filter as ff,
    inventory as inv,
    parser,
    recommender,
)


load_dotenv()


class GroceryAgent:
    """This is the main class of the agent application."""

    def __init__(
        self,
        parser_svc: parser.ParserService,
        recommender_svc: recommender.RecommenderService,
        inventory_svc: inv.InventoryService,
        fuzzy_filter_svc: ff.FuzzyFilterService,
        api_key: str,
        logger: logging.Logger,
    ) -> None:
        self.parser_svc = parser_svc
        self.recommender_svc = recommender_svc
        self.inventory_svc = inventory_svc
        self.fuzzy_filter_svc = fuzzy_filter_svc
        self.api_key = api_key
        self.logger = logger
        self.logger.debug("Successfully initialized the agent!")

    def load_catalog(self, source: str) -> None:
        """Load the store catalog."""
        self.logger.debug("Loading store catalog...")
        self.inventory_svc.load_catalog(source=source)
        self.logger.debug("Successfully loaded store catalog!")

    def process(self, filename: str, grocery_text: str) -> dict[str, Any]:
        """
        Process the grocery list depending on whether the OpenAI API key exists.
        If the key is present, the normal processing flow is followed, i.e.
            parser -> fuzzy filter -> recommender -> inventory
        Otherwise, the parser & recommender outputs are mocked, and fuzzy filter is skipped.
        """
        self.logger.debug(f"Processing grocery list, {filename=}, {grocery_text=}...")
        if not self.inventory_svc.catalog.catalog:
            self.logger.warning(
                "No store catalog found, no recommendations can be generated!"
            )
            return models.AgentRecommendationList(recommendations=[]).model_dump()

        if self.api_key:
            self.logger.debug("Will be using LLMs for parsing and recommending...")
            llm_recommendations = self._use_llms(grocery_text)
        else:
            self.logger.debug("Will be mocking parsing and recommending...")
            llm_recommendations = self._mock_llms(filename)
        resp = self.inventory_svc.get_final_recommendations(llm_recommendations)
        self.logger.debug("Successfully processed grocery list!")
        return resp.model_dump()

    def _use_llms(self, grocery_text: str) -> models.LLMRecommendationList:
        """Use LLMs for parsing and recommending."""
        llm_recommendations = models.LLMRecommendationList(recommendations=[])
        parsed_grocery_text = self.parser_svc.parse_grocery_text(grocery_text)
        if not parsed_grocery_text:
            self.logger.warning(
                f"Problem parsing the grocery list; setting {llm_recommendations=}!"
            )
            return llm_recommendations
        data = models.CatalogForFuzzyMatching(
            grocery_list=parsed_grocery_text, catalog=self.inventory_svc.catalog
        )
        pruned_catalog_list = self.fuzzy_filter_svc.filter_catalog(data)
        if not pruned_catalog_list:
            self.logger.warning(
                f"Problem pruning the store catalog; setting {llm_recommendations=}!"
            )
            return llm_recommendations
        product_recommendations = self.recommender_svc.recommend_products(
            pruned_catalog_list
        )
        if not product_recommendations:
            self.logger.warning(
                f"Problem retrieving product recommendations; setting {llm_recommendations=}!"
            )
        else:
            llm_recommendations = product_recommendations

        return llm_recommendations

    def _mock_llms(self, filename: str) -> models.LLMRecommendationList:
        """Mock responses of LLMs for parsing and recommending."""
        parsed_grocery_text = self.parser_svc.return_mocked_response(filename)
        llm_recommendations = self.recommender_svc.return_mocked_response(filename)
        if not parsed_grocery_text or not llm_recommendations:
            llm_recommendations = models.LLMRecommendationList(recommendations=[])
            self.logger.warning(
                f"Problem retrieving mocked response; setting {llm_recommendations=}!"
            )
        return llm_recommendations


def init_logger() -> logging.Logger:
    """Initialize the logger."""
    logger = logging.getLogger("GroceryAgent")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "{asctime} - {name} - {levelname} - {message}", style="{"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler("agent.log", mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def init_agent(catalog_source: str = "api") -> GroceryAgent:
    """Initialize the agent."""
    logger = init_logger()
    logger.info("Initializing agent...")

    api_key = os.getenv("OPENAI_API_KEY")
    basedir = pathlib.Path(__file__).parent.resolve()
    base_prompt_file = basedir / constants.PARSER_PROMPT_FILE
    dummy_responses_folder = basedir / constants.PARSER_DUMMY_RESPONSES
    model_name = constants.PARSER_LLM_MODEL
    parser_svc = parser.ParserService(
        api_key, model_name, base_prompt_file, dummy_responses_folder, logger
    )
    base_prompt_file = basedir / constants.RECOMMENDER_PROMPT_FILE
    dummy_responses_folder = basedir / constants.RECOMMENDER_DUMMY_RESPONSES
    model_name = constants.RECOMMENDER_LLM_MODEL
    recommender_svc = recommender.RecommenderService(
        api_key, model_name, base_prompt_file, dummy_responses_folder, logger
    )

    inventory_svc = inv.InventoryService(logger)
    fuzzy_filter_svc = ff.FuzzyFilterService(
        top_n=constants.FUZZY_FILTER_TOP_N,
        min_score=constants.FUZZY_FILTER_MIN_SCORE,
        logger=logger,
    )
    grocery_agent = GroceryAgent(
        parser_svc, recommender_svc, inventory_svc, fuzzy_filter_svc, api_key, logger
    )
    logger.info("Done initializing agent.")

    logger.info("Retrieving store catalog...")
    grocery_agent.load_catalog(source=catalog_source)
    logger.info("Done retrieving store catalog.")
    return grocery_agent


def main() -> None:
    """The application's entry point."""
    grocery_agent = init_agent(catalog_source="file")
    filename = "list01.txt"
    content = "<li/>3 packs of milk<li/>1 bag of sugar"

    grocery_agent.process(filename, content)


if __name__ == "__main__":
    main()
