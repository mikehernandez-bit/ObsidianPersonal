"""
ObsidianAcademia - Validadores
Funciones de validación para archivos, configuración y dependencias.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from src.utils.logger import get_logger

log = get_logger("validators")


def validate_file_exists(path: Path, description: str = "archivo") -> bool:
    """Verifica que un archivo exista."""
    if not path.exists():
        log.error(f"{description} no encontrado: {path}")
        return False
    if not path.is_file():
        log.error(f"{description} no es un archivo válido: {path}")
        return False
    return True


def validate_dir_exists(path: Path, description: str = "directorio") -> bool:
    """Verifica que un directorio exista."""
    if not path.exists():
        log.error(f"{description} no encontrado: {path}")
        return False
    if not path.is_dir():
        log.error(f"{description} no es un directorio válido: {path}")
        return False
    return True


def validate_executable(path: Path, description: str = "ejecutable") -> bool:
    """Verifica que un ejecutable exista y sea accesible."""
    if not path.exists():
        log.error(f"{description} no encontrado: {path}")
        return False
    if not path.suffix.lower() == ".exe":
        log.warning(f"{description} no tiene extensión .exe: {path}")
    return True


def validate_ffmpeg(ffmpeg_path: Path, ffprobe_path: Path) -> bool:
    """
    Valida que ffmpeg y ffprobe estén disponibles y funcionales.
    
    Returns:
        True si ambos están funcionales.
    """
    results = []

    for exe_path, name in [(ffmpeg_path, "ffmpeg"), (ffprobe_path, "ffprobe")]:
        if not exe_path.exists():
            log.error(f"{name} no encontrado en: {exe_path}")
            results.append(False)
            continue

        try:
            result = subprocess.run(
                [str(exe_path), "-version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                version_line = result.stdout.split("\n")[0]
                log.info(f"{name}: {version_line}")
                results.append(True)
            else:
                log.error(f"{name} retornó código de error: {result.returncode}")
                results.append(False)
        except FileNotFoundError:
            log.error(f"{name} no se puede ejecutar: {exe_path}")
            results.append(False)
        except subprocess.TimeoutExpired:
            log.error(f"{name} timeout al ejecutar")
            results.append(False)

    return all(results)


def validate_piper(
    piper_path: Path,
    model_path: Path,
    config_path: Optional[Path] = None,
) -> bool:
    """
    Valida que Piper y su modelo estén disponibles.
    
    Returns:
        True si Piper está listo para usar.
    """
    if not piper_path.exists():
        log.error(f"Piper no encontrado: {piper_path}")
        return False

    if not model_path.exists():
        log.error(f"Modelo Piper no encontrado: {model_path}")
        return False

    if config_path and not config_path.exists():
        log.warning(
            f"Archivo de configuración del modelo no encontrado: {config_path}. "
            "Piper intentará usar la configuración por defecto."
        )

    try:
        result = subprocess.run(
            [str(piper_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            log.error(f"Piper retornó código de error: {result.returncode}")
            return False
    except (FileNotFoundError, OSError):
        log.error(f"No se puede ejecutar Piper: {piper_path}")
        return False
    except subprocess.TimeoutExpired:
        log.error("Piper timeout al ejecutar")
        return False

    log.info(f"Piper: {piper_path}")
    log.info(f"Modelo: {model_path.name}")
    return True


def validate_ollama(endpoint: str, model: str) -> bool:
    """
    Valida que Ollama esté corriendo y el modelo esté disponible.
    
    Returns:
        True si Ollama responde y el modelo existe.
    """
    import requests

    # Verificar que Ollama está corriendo
    try:
        response = requests.get(f"{endpoint}/api/tags", timeout=5)
        if response.status_code != 200:
            log.error(f"Ollama respondió con código: {response.status_code}")
            return False
    except requests.ConnectionError:
        log.error(f"No se puede conectar a Ollama en: {endpoint}")
        log.info("Asegúrate de que Ollama esté corriendo (ollama serve)")
        return False
    except requests.Timeout:
        log.error("Timeout al conectar con Ollama")
        return False

    # Verificar que el modelo está disponible
    try:
        data = response.json()
        models = [m.get("name", "") for m in data.get("models", [])]

        if model in models or any(model in m for m in models):
            log.info(f"Ollama: modelo '{model}' disponible")
            return True
        else:
            log.error(f"Modelo '{model}' no encontrado. Modelos disponibles: {models}")
            log.info(f"Ejecuta: ollama pull {model}")
            return False
    except Exception as e:
        log.error(f"Error al verificar modelos de Ollama: {e}")
        return False


def validate_python_package(package_name: str) -> bool:
    """Verifica que un paquete Python esté instalado."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        log.warning(f"Paquete '{package_name}' no instalado")
        return False


def validate_all_dependencies() -> dict:
    """
    Valida todas las dependencias del sistema.
    
    Returns:
        Diccionario con el estado de cada dependencia.
    """
    status = {}

    # Paquetes Python requeridos
    required_packages = {
        "click": "click",
        "yaml": "pyyaml",
        "rich": "rich",
        "requests": "requests",
        "faster_whisper": "faster-whisper",
        "fitz": "PyMuPDF",
        "ollama": "ollama",
        "watchdog": "watchdog",
        "jinja2": "jinja2",
    }

    optional_packages = {
        "pytesseract": "pytesseract (OCR)",
        "PIL": "Pillow",
    }

    log.info("Verificando paquetes Python requeridos...")
    for import_name, display_name in required_packages.items():
        ok = validate_python_package(import_name)
        status[f"python.{display_name}"] = ok
        if ok:
            log.info(f"  ✓ {display_name}")
        else:
            log.error(f"  ✗ {display_name}")

    log.info("Verificando paquetes Python opcionales...")
    for import_name, display_name in optional_packages.items():
        ok = validate_python_package(import_name)
        status[f"python.{display_name}"] = ok
        if ok:
            log.info(f"  ✓ {display_name}")
        else:
            log.warning(f"  ○ {display_name} (opcional)")

    return status
