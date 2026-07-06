import logging
from pathlib import Path
from datetime import datetime
import sys

from scripts.config import LOGS_DIR

def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a logger with standard formatting.
    Writes logs to both console and a file in the logs directory.
    
    Args:
        name (str): Name of the logger, typically __name__.
        
    Returns:
        logging.Logger: Configured logger object.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger is already configured
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    
    # Create file handler
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"etl_pipeline_{timestamp}.log"
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    
    return logger
