import logging
import os
from datetime import datetime

def setup_logger(name="IDS_Logger", log_file="ids_system.log"):
    """Set up the logger for the IDS system."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger

def ensure_dirs():
    """Ensure required directories exist."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)

logger = setup_logger()
