"""
C0lorNote Logger Module

This module provides logging functionality for the C0lorNote application.
It configures both console and file logging with appropriate formatting and rotation.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Import settings to get the config directory
from src.config import settings

# Default log levels
DEFAULT_CONSOLE_LEVEL = logging.INFO
DEFAULT_FILE_LEVEL = logging.DEBUG

# Log format string
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log file settings
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3


def get_log_path():
    """
    Get the path for the log file
    
    Returns:
        str: Path to the log file
    """
    # Create the log directory if it doesn't exist
    log_dir = os.path.join(settings.APP_CONFIG_DIR, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Return the path to the log file
    return os.path.join(log_dir, "c0lornote.log")


def setup_logger(name="c0lornote", console_level=None, file_level=None):
    """
    Set up the logger with console and file handlers
    
    Args:
        name (str): Logger name
        console_level: Logging level for the console handler
        file_level: Logging level for the file handler
        
    Returns:
        logging.Logger: Configured logger object
    """
    if console_level is None:
        console_level = DEFAULT_CONSOLE_LEVEL
    
    if file_level is None:
        file_level = DEFAULT_FILE_LEVEL
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set to lowest level to capture all messages
    
    # Remove existing handlers if any
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    try:
        # File handler with rotation
        log_path = get_log_path()
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Log file configured at: {log_path}")
    
    except Exception as e:
        logger.error(f"Failed to setup file logging: {e}")
    
    return logger


def get_module_logger(module_name):
    """
    Get a logger for a specific module
    
    Args:
        module_name (str): Module name (usually __name__)
        
    Returns:
        logging.Logger: Logger for the module
    """
    return logging.getLogger(f"c0lornote.{module_name}")

