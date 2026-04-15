import logging
import os
from pathlib import Path
from typing import Optional

DEFAULT_LOG_FILE = Path(__file__).resolve().parent.parent / "download_bi.log"
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(log_file: Optional[str] = None, log_level: Optional[str] = None) -> None:
    """Configura logging para console e arquivo."""
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")

    path = Path(log_file) if log_file else DEFAULT_LOG_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    file_handler = logging.FileHandler(path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    root_logger.info("Logging inicializado. Arquivo de log: %s", path)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Retorna logger nomeado para um módulo."""
    return logging.getLogger(name)
