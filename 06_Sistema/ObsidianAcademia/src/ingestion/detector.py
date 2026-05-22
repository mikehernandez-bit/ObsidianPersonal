"""
ObsidianAcademia - Detector de Archivos
Detecta el tipo de archivo de entrada basándose en su extensión.
"""

from pathlib import Path
from typing import List

from src.config.constants import EXTENSION_MAP, FileType
from src.utils.logger import get_logger

log = get_logger("detector")


def detect_file_type(file_path: Path) -> FileType:
    """
    Detecta el tipo de archivo basándose en su extensión.
    
    Args:
        file_path: Ruta del archivo.
    
    Returns:
        FileType enum correspondiente.
    """
    ext = file_path.suffix.lower()
    file_type = EXTENSION_MAP.get(ext, FileType.UNKNOWN)
    log.debug(f"Detectado: {file_path.name} → {file_type.value}")
    return file_type


def classify_files(file_paths: List[Path]) -> dict:
    """
    Clasifica una lista de archivos por tipo.
    
    Args:
        file_paths: Lista de rutas de archivos.
    
    Returns:
        Diccionario {FileType: [paths]}.
    """
    classified = {ft: [] for ft in FileType}

    for fp in file_paths:
        ft = detect_file_type(fp)
        classified[ft].append(fp)

    # Log resumen
    for ft, paths in classified.items():
        if paths:
            log.info(f"  {ft.value}: {len(paths)} archivo(s)")

    return classified


def find_files_in_dir(
    directory: Path,
    file_type: FileType = None,
    recursive: bool = False,
) -> List[Path]:
    """
    Busca archivos en un directorio, opcionalmente filtrados por tipo.
    
    Args:
        directory: Directorio donde buscar.
        file_type: Si se especifica, solo retorna archivos de ese tipo.
        recursive: Si True, busca recursivamente.
    
    Returns:
        Lista de rutas de archivos encontrados.
    """
    if not directory.is_dir():
        log.error(f"No es un directorio: {directory}")
        return []

    pattern = "**/*" if recursive else "*"
    files = []

    for f in directory.glob(pattern):
        if not f.is_file():
            continue

        if file_type is None:
            ft = detect_file_type(f)
            if ft != FileType.UNKNOWN:
                files.append(f)
        else:
            ft = detect_file_type(f)
            if ft == file_type:
                files.append(f)

    log.debug(f"Encontrados {len(files)} archivos en {directory}")
    return sorted(files)
