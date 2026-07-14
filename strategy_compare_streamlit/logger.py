"""
Logging Module
"""

import logging

from pathlib import Path


###########################################################################
# LOGGER
###########################################################################

class StrategyLogger:

    def __init__(

        self,

        log_directory="logs",

        log_name="strategy_compare.log"

    ):

        self.log_directory = Path(

            log_directory

        )

        self.log_directory.mkdir(

            parents=True,

            exist_ok=True

        )

        self.log_file = self.log_directory / log_name

        self.logger = logging.getLogger(

            "StrategyCompare"

        )

        self.logger.setLevel(

            logging.INFO

        )

        if not self.logger.handlers:

            formatter = logging.Formatter(

                "%(asctime)s | %(levelname)s | %(message)s"

            )

            file_handler = logging.FileHandler(

                self.log_file,

                mode="a",

                encoding="utf-8"

            )

            file_handler.setFormatter(

                formatter

            )

            console_handler = logging.StreamHandler()

            console_handler.setFormatter(

                formatter

            )

            self.logger.addHandler(

                file_handler

            )

            self.logger.addHandler(

                console_handler

            )

    ###########################################################################
    # INFO
    ###########################################################################

    def info(

        self,

        message

    ):

        self.logger.info(

            message

        )

    ###########################################################################
    # WARNING
    ###########################################################################

    def warning(

        self,

        message

    ):

        self.logger.warning(

            message

        )

    ###########################################################################
    # ERROR
    ###########################################################################

    def error(

        self,

        message

    ):

        self.logger.error(

            message

        )

    ###########################################################################
    # EXCEPTION
    ###########################################################################

    def exception(

        self,

        message

    ):

        self.logger.exception(

            message

        )

    ###########################################################################
    # DEBUG
    ###########################################################################

    def debug(

        self,

        message

    ):

        self.logger.debug(

            message

        )

    ###########################################################################
    # START
    ###########################################################################

    def start(

        self,

        module

    ):

        self.info(

            f"Started: {module}"

        )

    ###########################################################################
    # FINISH
    ###########################################################################

    def finish(

        self,

        module

    ):

        self.info(

            f"Completed: {module}"

        )

    ###########################################################################
    # SEPARATOR
    ###########################################################################

    def separator(self):

        self.info(

            "-" * 80

        )