"""
ObsidianAcademia - Vault Writer
Escribe archivos .md directamente al vault de Obsidian.
"""

from pathlib import Path
from typing import Optional

from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.utils.paths import ensure_dir, get_unique_path

log = get_logger("vault_writer")


class VaultWriter:
    """Escribe notas Markdown directamente al filesystem del vault."""

    def __init__(self):
        settings = get_settings()
        self.vault_root = settings.vault_path

    def write_note(
        self,
        relative_path: str,
        content: str,
        overwrite: bool = False,
    ) -> Optional[Path]:
        """
        Escribe una nota Markdown en el vault.
        
        Args:
            relative_path: Ruta relativa dentro del vault (ej: "01_Universidad/Curso_01/nota.md").
            content: Contenido Markdown de la nota.
            overwrite: Si True, sobreescribe si existe.
        
        Returns:
            Ruta absoluta del archivo creado, o None si falla.
        """
        full_path = self.vault_root / relative_path.replace("/", "\\")
        return self._write_file(full_path, content, overwrite)

    def write_note_absolute(
        self,
        absolute_path: Path,
        content: str,
        overwrite: bool = False,
    ) -> Optional[Path]:
        """
        Escribe una nota usando ruta absoluta.
        
        Args:
            absolute_path: Ruta absoluta del archivo.
            content: Contenido Markdown.
            overwrite: Si True, sobreescribe.
        
        Returns:
            Ruta del archivo creado, o None si falla.
        """
        return self._write_file(absolute_path, content, overwrite)

    def _write_file(
        self,
        path: Path,
        content: str,
        overwrite: bool = False,
    ) -> Optional[Path]:
        """Escribe un archivo con manejo de errores."""
        try:
            ensure_dir(path.parent)

            if path.exists() and not overwrite:
                path = get_unique_path(path)
                log.info(f"Archivo existente, renombrado a: {path.name}")

            path.write_text(content, encoding="utf-8")
            log.debug(f"Nota escrita: {path}")
            return path

        except PermissionError:
            log.error(f"Sin permisos para escribir: {path}")
            return None
        except OSError as e:
            log.error(f"Error al escribir nota: {e}")
            return None

    def create_directory(self, relative_path: str) -> Optional[Path]:
        """
        Crea un directorio dentro del vault.
        
        Args:
            relative_path: Ruta relativa del directorio.
        
        Returns:
            Ruta absoluta del directorio creado.
        """
        full_path = self.vault_root / relative_path.replace("/", "\\")
        try:
            return ensure_dir(full_path)
        except Exception as e:
            log.error(f"Error al crear directorio: {e}")
            return None

    def note_exists(self, relative_path: str) -> bool:
        """Verifica si una nota existe en el vault."""
        full_path = self.vault_root / relative_path.replace("/", "\\")
        return full_path.exists()

    def read_note(self, relative_path: str) -> Optional[str]:
        """Lee el contenido de una nota existente."""
        full_path = self.vault_root / relative_path.replace("/", "\\")
        if not full_path.exists():
            return None
        try:
            return full_path.read_text(encoding="utf-8")
        except Exception as e:
            log.error(f"Error al leer nota: {e}")
            return None

    def append_to_note(self, relative_path: str, content: str) -> bool:
        """Añade contenido al final de una nota existente."""
        full_path = self.vault_root / relative_path.replace("/", "\\")
        try:
            if full_path.exists():
                existing = full_path.read_text(encoding="utf-8")
                full_path.write_text(
                    existing + "\n" + content, encoding="utf-8"
                )
            else:
                ensure_dir(full_path.parent)
                full_path.write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            log.error(f"Error al añadir a nota: {e}")
            return False
