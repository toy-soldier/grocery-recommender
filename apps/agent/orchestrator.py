"""This module contains all orchestration logic."""

import logging
import os
import pathlib
from dotenv import load_dotenv

from apps.agent.services import fuzzy_filter as ff, inventory as inv, parser, recommender
from apps.agent import constants

# reads variables from a .env file and sets them in os.environ
load_dotenv()


class GroceryAgent:
    """This is the main class of the agent application."""

    def __init__(
        self,
        parser_svc: parser.ParserService,
        recommender_svc: recommender.RecommenderService,
        inventory_svc: inv.InventoryService,
        fuzzy_filter_svc: ff.FuzzyFilterService,
        logger: logging.Logger,
    ) -> None:
        self.parser_svc = parser_svc
        self.recommender_svc = recommender_svc
        self.inventory_svc = inventory_svc
        self.fuzzy_filter_svc = fuzzy_filter_svc
        self.logger = logger
        self.logger.debug("Successfully initialized the agent!")

    def load_catalog(self) -> None:
        self.logger.debug("Loading store catalog...")
        self.inventory_svc.load_catalog()
        self.logger.debug("Successfully loaded store catalog!")

    def process(self, filename: str, grocery_text: str) -> dict:
        self.logger.debug(f"Processing grocery list, {filename=}, {grocery_text=}...")
        return self.inventory_svc.get_final_recommendations(llm_recommendations={})


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


def init_agent() -> GroceryAgent:
    """Initialize the agent."""
    logger = init_logger()
    logger.info("Initializing agent...")

    api_key = os.getenv("OPENAI_API_KEY")
    basedir = pathlib.Path(__file__).parent.resolve()
    prompt_file = basedir / constants.PARSER_PROMPT_FILE
    parser_svc = parser.ParserService(api_key, prompt_file, logger)
    prompt_file = basedir / constants.RECOMMENDER_PROMPT_FILE
    recommender_svc = recommender.RecommenderService(api_key, prompt_file, logger)

    inventory_svc = inv.InventoryService(logger)
    fuzzy_filter_svc = ff.FuzzyFilterService(logger)

    grocery_agent = GroceryAgent(
        parser_svc, recommender_svc, inventory_svc, fuzzy_filter_svc, logger
    )
    logger.info("Done initializing agent.")

    logger.info("Retrieving store catalog...")
    grocery_agent.load_catalog()
    logger.info("Done retrieving store catalog.")
    return grocery_agent


def main() -> None:
    """The application's entry point."""
    grocery_agent = init_agent()
    filename = "list.txt"
    content = "<li/>3 packs of milk<li/>1 bag of sugar"

    grocery_agent.process(filename, content)


if __name__ == "__main__":
    main()
