"""
ObsidianAcademia - File Manager
Gestión de archivos de entrada: copiar, mover y organizar.
"""

import shutil
from pathlib import Path
from typing import Optional

from src.config.settings import get_settings
from src.config.constants import FileType
from src.ingestion.detector import detect_file_type
from src.utils.logger import get_logger
from src.utils.paths import ensure_dir, get_unique_path

log = get_logger("file_manager")


def copy_to_vault(
    source_path: Path,
    destination_dir: Optional[Path] = None,
    overwrite: bool = False,
) -> Optional[Path]:
    """
    Copia un archivo al vault de Obsidian en la carpeta apropiada según su tipo.
    
    Args:
        source_path: Ruta del archivo fuente.
        destination_dir: Directorio destino. Si es None, se determina por tipo.
        overwrite: Si True, sobreescribe archivos existentes.
    
    Returns:
        Ruta del archivo copiado en el vault, o None si falla.
    """
    if not source_path.exists():
        log.error(f"Archivo fuente no encontrado: {source_path}")
        return None

    settings = get_settings()

    # Determinar directorio destino si no se especificó
    if destination_dir is None:
        file_type = detect_file_type(source_path)
        type_to_dir = {
            FileType.AUDIO: settings.input_audios,
            FileType.VIDEO: settings.input_videos,
            FileType.IMAGE: settings.input_imagenes,
            FileType.PDF: settings.input_pdfs,
        }
        destination_dir = type_to_dir.get(file_type, settings.vault_path / "03_Materiales" / "Otros")

    ensure_dir(destination_dir)
    dest_path = destination_dir / source_path.name

    if dest_path.exists() and not overwrite:
        dest_path = get_unique_path(dest_path)

    try:
        shutil.copy2(source_path, dest_path)
        log.info(f"Copiado: {source_path.name} → {dest_path}")
        return dest_path
    except Exception as e:
        log.error(f"Error al copiar archivo: {e}")
        return None


def organize_session_files(
    file_paths: list,
    course_id: str,
    week: int,
    session_type: str,
) -> dict:
    """
    Organiza archivos de entrada para una sesión, copiándolos al vault.
    
    Args:
        file_paths: Lista de rutas de archivos de entrada.
        course_id: ID del curso.
        week: Número de semana.
        session_type: "Teoria" o "Practica".
    
    Returns:
        Diccionario con archivos organizados por tipo.
    """
    from src.utils.paths import build_session_path

    settings = get_settings()
    session_dir = build_session_path(settings.vault_path, course_id, week, session_type)
    ensure_dir(session_dir)

    organized = {
        "audios": [],
        "videos": [],
        "images": [],
        "pdfs": [],
        "markdown": [],
        "other": [],
    }

    for fp in file_paths:
        fp = Path(fp)
        if not fp.exists():
            log.warning(f"Archivo no encontrado, omitido: {fp}")
            continue

        file_type = detect_file_type(fp)
        # Copiar al directorio de la sesión
        dest = session_dir / fp.name
        if dest.exists():
            dest = get_unique_path(dest)

        try:
            shutil.copy2(fp, dest)
            type_key = {
                FileType.AUDIO: "audios",
                FileType.VIDEO: "videos",
                FileType.IMAGE: "images",
                FileType.PDF: "pdfs",
                FileType.MARKDOWN: "markdown",
            }.get(file_type, "other")

            organized[type_key].append(dest)
            log.debug(f"Organizado: {fp.name} → {type_key}")
        except Exception as e:
            log.error(f"Error al organizar {fp.name}: {e}")

    total = sum(len(v) for v in organized.values())
    log.info(f"Archivos organizados: {total} en {session_dir}")
    return organized
