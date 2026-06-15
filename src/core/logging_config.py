import logging
import sys
from src.core.config import settings


def setup_logging():
    level = logging.DEBUG if settings.debug else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # 屏蔽三方库的噪音日志
    for noisy in ("httpx", "chromadb", "sentence_transformers", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
