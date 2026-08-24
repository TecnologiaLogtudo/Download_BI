import logging
import os
import sys
from pathlib import Path
from typing import Optional

DEFAULT_LOG_FILE = Path(__file__).resolve().parent.parent / "download_bi.log"
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_LOGGING_CONFIGURED = False


class FlushingStreamHandler(logging.StreamHandler):
    """StreamHandler que executa flush a cada mensagem gravada para visibilidade em tempo real no terminal/scheduler."""
    def emit(self, record):
        super().emit(record)
        self.flush()


def configure_logging(log_file: Optional[str] = None, log_level: Optional[str] = None) -> None:
    """Configura logging para console (sys.stdout com flush automático e UTF-8) e arquivo."""
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    # Força reconfiguração dos streams no Windows para UTF-8 sem erros de encoding
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    path = Path(log_file) if log_file else DEFAULT_LOG_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console Handler usando sys.stdout + flush imediato
    console_handler = FlushingStreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # File Handler com UTF-8
    file_handler = logging.FileHandler(path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Limpa handlers anteriores para evitar duplicação ou bloqueios por inicializações prévias
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    _LOGGING_CONFIGURED = True
    root_logger.info("Logging inicializado. Arquivo de log: %s", path)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Retorna logger nomeado garantindo que o sistema de logs foi inicializado."""
    if not _LOGGING_CONFIGURED:
        configure_logging()
    return logging.getLogger(name)

