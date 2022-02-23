import logging

logger = logging.getLogger("soniccontrol")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('soniccontrol.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
