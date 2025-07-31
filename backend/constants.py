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

STREAMFLOW_VARIABLE_IDS = {
    'seven_day_variable_id': 1,
    'stage_variable_id': 2
}
CLIMATE_VARIABLE_IDS = {
    'snow_depth_variable_id': 5,
    'temperature_variable_ids': [6, 8],
    'swe_variable_id': 16,
    'msp_variable_id': 19,
    'precipitation_variable_id': 27
}
