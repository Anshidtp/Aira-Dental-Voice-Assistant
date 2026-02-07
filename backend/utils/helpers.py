import sys
from loguru import logger
from ..config import settings


def setup_logger():
    """Configure logger with appropriate settings"""
    
    # Remove default logger
    logger.remove()
    
    # Add console logger with appropriate level
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
    )
    
    # Add file logger for errors in production
    if settings.is_production:
        logger.add(
            "logs/error.log",
            rotation="500 MB",
            retention="10 days",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        )
        
        # Add file logger for all logs
        logger.add(
            "logs/app.log",
            rotation="500 MB",
            retention="7 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        )
    
    return logger


# Initialize logger
log = setup_logger()