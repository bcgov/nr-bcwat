import logging

def setup_logger(name, level=logging.INFO):
    """Set up a logger with the given name and level."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        # Create console handler and set level
        ch = logging.StreamHandler()
        ch.setLevel(level)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s %(message)s')

        # Add formatter to console handler
        ch.setFormatter(formatter)

        # Add console handler to logger
        logger.addHandler(ch)

    return logger

logger = setup_logger("logger")
