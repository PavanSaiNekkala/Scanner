"""
Logging Module
"""

import logging

from logging.handlers import RotatingFileHandler

from pathlib import Path


###########################################################################
# LOGGER
###########################################################################

class StrategyLogger:

    def __init__(

        self,

        log_directory="logs",

        log_name="strategy_compare.log",

        level=logging.INFO

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

            level

        )

        self.logger.propagate = False

        if self.logger.handlers:

            self.logger.handlers.clear()

        formatter = logging.Formatter(

            "%(asctime)s | %(levelname)-8s | %(message)s",

            "%Y-%m-%d %H:%M:%S"

        )

        #######################################################################
        # FILE HANDLER
        #######################################################################

        file_handler = RotatingFileHandler(

            self.log_file,

            maxBytes=5 * 1024 * 1024,

            backupCount=5,

            encoding="utf-8"

        )

        file_handler.setFormatter(

            formatter

        )

        #######################################################################
        # CONSOLE HANDLER
        #######################################################################

        console_handler = logging.StreamHandler()

        console_handler.setFormatter(

            formatter

        )

        #######################################################################
        # REGISTER
        #######################################################################

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
    # START
    ###########################################################################

    def start(

        self,

        module

    ):

        self.separator()

        self.info(

            f"Started : {module}"

        )

    ###########################################################################
    # FINISH
    ###########################################################################

    def finish(

        self,

        module

    ):

        self.info(

            f"Completed : {module}"

        )

        self.separator()

    ###########################################################################
    # SEPARATOR
    ###########################################################################

    def separator(

        self

    ):

        self.info(

            "=" * 80

        )

    ###########################################################################
    # PIPELINE SUMMARY
    ###########################################################################

    def pipeline_summary(

        self,

        reports,

        ranked,

        recommendations,

        overlap

    ):

        self.separator()

        self.info(

            "Pipeline Summary"

        )

        self.info(

            f"Reports Loaded      : {reports}"

        )

        self.info(

            f"Ranked Strategies   : {ranked}"

        )

        self.info(

            f"Recommendations     : {recommendations}"

        )

        self.info(

            f"Overlap Rows        : {overlap}"

        )

        self.separator()