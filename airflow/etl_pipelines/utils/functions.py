from etl_pipelines.utils.constants import loggers
import logging

def setup_logging(name = 'airflow'):
    if name in loggers:
        return loggers[name]
    else:
        FORMAT = "[%(asctime)s] [%(levelname)s] [%(filename)s] [%(funcName)s()] [%(lineno)s]: %(message)s"
        logging.basicConfig(format=FORMAT)
        logger = logging.getLogger('airflow')
        logger.setLevel(logging.DEBUG)

        loggers[name] = logger

        return logger
