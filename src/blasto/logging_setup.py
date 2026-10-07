import logging
import sys


def setup_logging(level: str) -> None:  # call once, at startup
    logging.basicConfig(  # configure the root logger, which all loggers report to
        level=level,  # the threshold, e.g. "INFO": lower levels are hidden
        format="%(asctime)s %(levelname)s %(name)s %(message)s",  # time, level, logger name, message
        stream=sys.stdout,  # write to stdout (the default would be stderr)
    )
