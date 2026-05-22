"""
ObsidianAcademia - Logger
Configuración centralizada de logging con Rich para consola y archivo.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Variable global para evitar doble inicialización
_logger_initialized = False


def setup_logger(
    name: str = "academia",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
) -> logging.Logger:
    """
    Configura y retorna un logger con salida a consola (Rich) y archivo.
    
    Args:
        name: Nombre del logger.
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR).
        log_file: Ruta del archivo de log. Si es None, no se loguea a archivo.
        console: Si True, también loguea a consola.
    
    Returns:
        Logger configurado.
    """
    global _logger_initialized

    logger = logging.getLogger(name)

    # Evitar duplicar handlers si ya se inicializó
    if _logger_initialized:
        return logger

    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Formato para archivo
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler de consola con Rich si está disponible
    if console:
        try:
            from rich.logging import RichHandler

            console_handler = RichHandler(
                level=log_level,
                show_path=False,
                markup=True,
                rich_tracebacks=True,
            )
            console_handler.setFormatter(logging.Formatter("%(message)s"))
        except ImportError:
            # Fallback a handler estándar si Rich no está instalado
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(file_formatter)

        logger.addHandler(console_handler)

    # Handler de archivo
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(
            log_path, encoding="utf-8", mode="a"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    _logger_initialized = True
    return logger


def get_logger(name: str = "academia") -> logging.Logger:
    """Obtiene un logger hijo con el nombre dado."""
    return logging.getLogger(f"academia.{name}")
