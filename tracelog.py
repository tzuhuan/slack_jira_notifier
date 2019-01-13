import logging

LOG_FILE = "case_notifier.log"
LOGGER_NAME = "case_notifier"

def getLogger():
    fmt = "%(asctime)s [%(levelname)s] %(message)s @ func:%(funcName)s file:%(filename)s line:%(lineno)s "
    logging.basicConfig(level=logging.INFO, format=fmt, filename=LOG_FILE)
    logger = logging.getLogger(LOGGER_NAME)
    
    return logger
    