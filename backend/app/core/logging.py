import sys
from loguru import logger
from app.config import get_settings

settings = get_settings()

logger.remove()

log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

logger.add(
    sys.stdout,
    level="DEBUG" if settings.DEBUG else "INFO",
    format=log_format,
    colorize=True,
    enqueue=True,
)


def get_logger(name: str):
    return logger.bind(name=name)