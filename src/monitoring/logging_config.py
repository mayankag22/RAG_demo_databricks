from loguru import logger
import os

os.makedirs("logs", exist_ok=True)
logger.add("logs/app.log", rotation="5 MB", retention="7 days", level="INFO")

__all__ = ["logger"]
# This module sets up logging configuration for the application using loguru.