"""
ObsidianAcademia - Utilidades de Rutas
Funciones para manejo seguro de rutas en Windows con pathlib.
"""

import re
import unicodedata
from pathlib import Path
from typing import Optional


def sanitize_filename(name: str) -> str:
    """
    Sanitiza un nombre para usarlo como archivo o carpeta en Windows.
    Remueve caracteres ilegales, normaliza Unicode y reemplaza espacios.
    
    Args:
        name: Nombre original.
    
    Returns:
        Nombre sanitizado listo para usar en el filesystem.
    """
    # Normalizar Unicode (ñ, acentos, etc. se mantienen)
    name = unicodedata.normalize("NFC", name)

    # Reemplazar caracteres ilegales en Windows
    illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
    name = re.sub(illegal_chars, "_", name)

    # Reemplazar espacios múltiples por underscore
    name = re.sub(r"\s+", "_", name.strip())

    # Remover puntos al final (Windows no los permite en nombres de carpeta)
    name = name.rstrip(".")

    # Limitar longitud (Windows MAX_PATH es 260, dejamos margen)
    if len(name) > 100:
        name = name[:100]

    return name


def ensure_dir(path: Path) -> Path:
    """
    Crea un directorio y sus padres si no existen.
    
    Args:
        path: Ruta del directorio a crear.
    
    Returns:
        La misma ruta, confirmada como existente.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_vault_path(vault_root: Path, relative_path: str) -> Path:
    """
    Resuelve una ruta relativa dentro del vault.
    
    Args:
        vault_root: Ruta absoluta raíz del vault de Obsidian.
        relative_path: Ruta relativa dentro del vault.
    
    Returns:
        Ruta absoluta resuelta.
    """
    # Normalizar separadores para Windows
    relative_path = relative_path.replace("/", "\\")
    return vault_root / relative_path


def format_path_for_obsidian(path: Path, vault_root: Path) -> str:
    """
    Convierte una ruta absoluta a ruta relativa para uso en links de Obsidian.
    Obsidian usa forward slashes en sus links internos.
    
    Args:
        path: Ruta absoluta del archivo.
        vault_root: Ruta raíz del vault.
    
    Returns:
        Ruta relativa con forward slashes para Obsidian.
    """
    try:
        relative = path.relative_to(vault_root)
        return str(relative).replace("\\", "/")
    except ValueError:
        # Si no está dentro del vault, retornar ruta absoluta
        return str(path).replace("\\", "/")


def get_unique_path(path: Path) -> Path:
    """
    Si el archivo ya existe, añade un sufijo numérico para evitar sobreescritura.
    
    Args:
        path: Ruta original del archivo.
    
    Returns:
        Ruta única (la original si no existe conflicto).
    """
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1

    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


def build_session_path(
    vault_root: Path,
    course_id: str,
    week: int,
    session_type: str,
    filename: Optional[str] = None,
) -> Path:
    """
    Construye la ruta para un archivo de sesión universitaria.
    
    Ejemplo: vault/01_Universidad/Curso_CS901/Semana_03/Teoria/resumen.md
    
    Args:
        vault_root: Raíz del vault.
        course_id: ID del curso (ej: "curso_01").
        week: Número de semana (1-16).
        session_type: "Teoria" o "Practica".
        filename: Nombre del archivo (opcional).
    
    Returns:
        Ruta construida.
    """
    week_str = f"Semana_{week:02d}"
    path = vault_root / "01_Universidad" / f"Curso_{course_id}" / week_str / session_type

    if filename:
        path = path / filename

    return path


def build_coursera_path(
    vault_root: Path,
    program: Optional[str],
    course: str,
    module: Optional[str] = None,
    lesson: Optional[str] = None,
    filename: Optional[str] = None,
) -> Path:
    """
    Construye la ruta para contenido de Coursera.
    
    Args:
        vault_root: Raíz del vault.
        program: Nombre del programa (None para curso individual).
        course: Nombre del curso.
        module: Nombre del módulo.
        lesson: Nombre de la lección.
        filename: Nombre del archivo.
    
    Returns:
        Ruta construida.
    """
    base = vault_root / "02_Coursera"

    if program:
        base = base / f"Programa_{sanitize_filename(program)}"

    base = base / f"Curso_{sanitize_filename(course)}"

    if module:
        base = base / f"Modulo_{sanitize_filename(module)}"

    if lesson:
        base = base / f"Leccion_{sanitize_filename(lesson)}"

    if filename:
        base = base / filename

    return base
