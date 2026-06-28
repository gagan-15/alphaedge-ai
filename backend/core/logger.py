"""
File Name:
    logger.py

Purpose:
    Configure and provide a centralized logger
    for the AlphaEdge AI application.

Author:
    Gagan Devali

Project:
    AlphaEdge AI
"""

import logging
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("AlphaEdgeAI")
logger.setLevel(logging.INFO)

if not logger.handlers:

    # Create a console handler to display logs in the terminal.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a formatter for log messages.
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Apply the formatter to the console handler.
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create a file handler to save logs in a file.
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
