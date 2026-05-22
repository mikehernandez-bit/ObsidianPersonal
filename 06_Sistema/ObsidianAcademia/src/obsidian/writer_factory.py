"""
ObsidianAcademia - Writer Factory
Selecciona el escritor apropiado: REST API si disponible, filesystem como fallback.
"""

from src.config.settings import get_settings
from src.utils.logger import get_logger

log = get_logger("writer_factory")


def get_writer():
    """
    Retorna el escritor apropiado según la configuración y disponibilidad.
    
    Lógica:
    1. Si use_rest_api=True en config → intenta REST API
    2. Si REST API no responde → fallback a escritura directa
    3. Si use_rest_api=False → escritura directa
    
    Returns:
        VaultWriter o ObsidianRestApi (misma interfaz).
    """
    settings = get_settings()

    if settings.use_rest_api:
        from src.obsidian.rest_api import ObsidianRestApi

        api = ObsidianRestApi()
        if api.is_available():
            log.info("Usando: Obsidian REST API")
            return api
        else:
            log.warning(
                "REST API configurada pero no disponible. "
                "Usando escritura directa al filesystem."
            )

    from src.obsidian.vault_writer import VaultWriter

    log.info("Usando: Escritura directa al vault")
    return VaultWriter()
