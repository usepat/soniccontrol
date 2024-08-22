import logging

def get_base_logger(logger: logging.Logger) -> logging.Logger:
    try:
        base_logger_name = logger.name.split(".").pop(0)
    except IndexError:
        base_logger_name = ""
    
    return logging.getLogger(base_logger_name)