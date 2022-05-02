import logging
import os

if not os.path.exists("Logs"):
    os.mkdir('Logs')

logger = logging.getLogger("soniccontrol")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s\t%(name)s\t%(funcName)s\t%(message)s')
file_handler = logging.FileHandler('Logs//soniccontrol.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# def log_it(message: str) -> None:

status_logger = logging.getLogger("statuslogger")
status_logger.setLevel(logging.DEBUG)
status_formatter = logging.Formatter('%(asctime)s\t%(message)s')
status_log_file_handler = logging.FileHandler('Logs//statuslog.csv')
status_log_file_handler.setFormatter(status_formatter)
status_logger.addHandler(status_log_file_handler)
    
