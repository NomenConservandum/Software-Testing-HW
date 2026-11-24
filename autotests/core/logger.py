from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Iterable

from core.config import PROJECT_ROOT
from core.masking import mask_text

LOGS_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOGS_DIR / "test.log"


class MaskingFilter(logging.Filter):
    """Фильтр логгера для обязательного маскирования чувствительных данных."""

    def __init__(self, secrets: Iterable[str] = ()) -> None:
        super().__init__()
        self._secrets = tuple(secrets)

    def update_secrets(self, secrets: Iterable[str]) -> None:
        self._secrets = tuple(secrets)

    def filter(self, record: logging.LogRecord) -> bool:
        rendered = record.getMessage()
        record.msg = mask_text(rendered, self._secrets)
        record.args = ()
        return True


_mask_filter = MaskingFilter()


def setup_logger(level_name: str = "INFO", secrets: Iterable[str] = ()) -> logging.Logger:
    """Настраивает единый логгер проекта с уровнями DEBUG/INFO/WARNING/ERROR."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    _mask_filter.update_secrets(secrets)

    logger = logging.getLogger("autotests")
    level = getattr(logging, level_name.upper(), logging.INFO)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(_mask_filter)

        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.addFilter(_mask_filter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    for handler in logger.handlers:
        handler.setLevel(level)

    return logger


def get_logger(name: str = "autotests") -> logging.Logger:
    return logging.getLogger(name)


def read_recent_logs(tail_lines: int = 80) -> str:
    """Возвращает последние строки замаскированного лог-файла для отчёта."""
    if not LOG_FILE.exists():
        return ""
    lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-tail_lines:])
