import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )

    # Silence overly verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if not settings.DEBUG else logging.INFO
    )


logger = logging.getLogger("talentforge")
