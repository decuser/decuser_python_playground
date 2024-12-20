import logging

def setup_logger(debug, name, log_file):
    """
    Configures a logger with both console and file handlers.

    :param debug: debug flag from configuration
    :param name: Name of the logger.
    :param log_file: Path to the log file.
    :return: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(log_file)

    # Set handler levels
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Set formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers if not already added
    if not logger.hasHandlers():
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
