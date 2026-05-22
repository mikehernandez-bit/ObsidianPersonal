"""
ObsidianAcademia - REST API Client
Cliente para Obsidian Local REST API (opcional).
Implementa la misma interfaz que VaultWriter para intercambiabilidad.
"""

from pathlib import Path
from typing import Optional

import requests

from src.config.settings import get_settings
from src.utils.logger import get_logger

log = get_logger("rest_api")


class ObsidianRestApi:
    """Cliente para Obsidian Local REST API."""

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.rest_api_url.rstrip("/")
        self.api_key = settings.rest_api_key
        self.vault_root = settings.vault_path
        self._available = None

    def _headers(self) -> dict:
        """Retorna headers para las peticiones HTTP."""
        headers = {
            "Content-Type": "text/markdown",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def is_available(self) -> bool:
        """
        Verifica si Obsidian Local REST API está disponible.
        Cachea el resultado para evitar checks repetidos.
        """
        if self._available is not None:
            return self._available

        try:
            response = requests.get(
                f"{self.base_url}/",
                headers=self._headers(),
                timeout=3,
            )
            self._available = response.status_code == 200
            if self._available:
                log.info("Obsidian REST API disponible")
            else:
                log.info(
                    f"Obsidian REST API respondió con código: {response.status_code}"
                )
        except requests.ConnectionError:
            self._available = False
            log.info("Obsidian REST API no disponible (connection refused)")
        except requests.Timeout:
            self._available = False
            log.info("Obsidian REST API no disponible (timeout)")

        return self._available

    def write_note(
        self,
        relative_path: str,
        content: str,
        overwrite: bool = False,
    ) -> Optional[Path]:
        """
        Crea o actualiza una nota vía REST API.
        
        Args:
            relative_path: Ruta relativa dentro del vault.
            content: Contenido Markdown.
            overwrite: Si True, sobreescribe (PUT). Si False, crea (POST).
        
        Returns:
            Ruta simulada del archivo, o None si falla.
        """
        # Normalizar path para la API (usa forward slashes)
        api_path = relative_path.replace("\\", "/")
        url = f"{self.base_url}/vault/{api_path}"

        try:
            if overwrite:
                response = requests.put(
                    url,
                    data=content.encode("utf-8"),
                    headers=self._headers(),
                    timeout=10,
                )
            else:
                # Intentar POST primero, si existe fallback a PUT
                response = requests.post(
                    url,
                    data=content.encode("utf-8"),
                    headers=self._headers(),
                    timeout=10,
                )

                # Si ya existe (409 Conflict), usar PUT
                if response.status_code == 409:
                    response = requests.put(
                        url,
                        data=content.encode("utf-8"),
                        headers=self._headers(),
                        timeout=10,
                    )

            if response.status_code in (200, 201, 204):
                log.debug(f"Nota escrita vía REST API: {api_path}")
                return self.vault_root / relative_path.replace("/", "\\")
            else:
                log.error(
                    f"REST API error ({response.status_code}): {response.text[:200]}"
                )
                return None

        except Exception as e:
            log.error(f"Error en REST API: {e}")
            return None

    def write_note_absolute(
        self,
        absolute_path: Path,
        content: str,
        overwrite: bool = False,
    ) -> Optional[Path]:
        """Escribe una nota usando ruta absoluta (convierte a relativa para API)."""
        try:
            relative = str(absolute_path.relative_to(self.vault_root))
            return self.write_note(relative, content, overwrite)
        except ValueError:
            log.error(f"Ruta fuera del vault: {absolute_path}")
            return None

    def read_note(self, relative_path: str) -> Optional[str]:
        """Lee una nota vía REST API."""
        api_path = relative_path.replace("\\", "/")
        url = f"{self.base_url}/vault/{api_path}"

        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            log.error(f"Error al leer nota vía API: {e}")
            return None

    def note_exists(self, relative_path: str) -> bool:
        """Verifica si una nota existe vía REST API."""
        content = self.read_note(relative_path)
        return content is not None
