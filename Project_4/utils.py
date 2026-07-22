"""Shared utilities: logging and condition-based waits."""
import logging
import time
from typing import Callable

LOG_FILE = "bot.log"


def setup_logging(name: str = "whatsapp_bot") -> logging.Logger:
    """Configure logging to both a file and the console."""
    logger = logging.getLogger(name)
    if logger.handlers:  # avoid duplicate handlers on re-import
        return logger

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)

    return logger


def wait_until(
    condition: Callable[[], bool],
    timeout: float = 30.0,
    interval: float = 0.5,
) -> bool:
    """Poll `condition` until it is truthy or `timeout` seconds elapse.

    Returns True if the condition became true, False on timeout. This
    replaces blind, fixed `time.sleep()` calls.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(interval)
    return False
