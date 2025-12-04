"""This module defines the FuzzyFilterService class."""

import logging

import rapidfuzz


class FuzzyFilterService:
    """This class is responsible for running fuzzy matching on the store inventory."""

    def __init__(self, logger: logging.Logger) -> None:
        child_logger = logger.getChild("FuzzyFilterService")
        self.logger = child_logger
        self.logger.debug("Finished initializing fuzzy matching service!")
