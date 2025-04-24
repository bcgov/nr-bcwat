import logging

def setup_logging():
    logger = logging.getLogger('airflow')
    logger.setLevel(logging.DEBUG)

    return logger
