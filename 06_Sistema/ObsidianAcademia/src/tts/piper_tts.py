"""
ObsidianAcademia - Text-to-Speech con Piper
Genera audio .wav a partir de texto usando Piper TTS local.
"""

import json
import subprocess
from pathlib import Path
from typing import Optional

from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.utils.paths import ensure_dir

log = get_logger("tts")


def _resolve_config_path(model_path: Path, configured_path: Optional[Path]) -> Optional[Path]:
    """Resuelve la ruta del config JSON del modelo Piper."""
    if configured_path:
        return configured_path
    return Path(f"{model_path}.json")


def _read_num_speakers(config_path: Path) -> Optional[int]:
    """Lee el numero de speakers desde el config JSON del modelo."""
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as error:
        log.warning(f"No se pudo leer el config de Piper ({config_path}): {error}")
        return None

    num_speakers = data.get("num_speakers")
    if isinstance(num_speakers, int):
        return num_speakers
    return None


def generate_audio(
    text: str,
    output_path: Path,
    length_scale: Optional[float] = None,
    sentence_silence: Optional[float] = None,
) -> Optional[Path]:
    """
    Genera un archivo de audio WAV a partir de texto usando Piper TTS.
    
    Args:
        text: Texto a convertir a audio.
        output_path: Ruta del archivo WAV de salida.
        length_scale: Velocidad de habla (1.0=normal, >1=más lento, <1=más rápido).
        sentence_silence: Segundos de silencio entre oraciones.
    
    Returns:
        Ruta del archivo de audio generado, o None si falla.
    """
    settings = get_settings()

    piper_exe = settings.piper_exe
    model_path = settings.piper_model
    config_path = _resolve_config_path(model_path, settings.piper_config)

    if not piper_exe.exists():
        log.error(f"Piper no encontrado: {piper_exe}")
        return None

    if not model_path.exists():
        log.error(f"Modelo Piper no encontrado: {model_path}")
        return None

    if config_path is None or not config_path.exists():
        log.error(f"Config de Piper no encontrado: {config_path}")
        return None

    if not text.strip():
        log.warning("Texto vacío, no se genera audio")
        return None

    # Parámetros con fallback a config
    if length_scale is None:
        length_scale = settings.piper_length_scale
    if sentence_silence is None:
        sentence_silence = settings.piper_sentence_silence

    ensure_dir(output_path.parent)

    # Construir comando Piper
    cmd = [
        str(piper_exe),
        "--model", str(model_path),
        "--output_file", str(output_path),
        "--length_scale", str(length_scale),
        "--sentence_silence", str(sentence_silence),
        "--config", str(config_path),
    ]

    num_speakers = _read_num_speakers(config_path)
    if num_speakers is None or num_speakers > 1:
        cmd.extend(["--speaker", str(settings.piper_speaker)])

    log.info(f"Generando audio TTS: {output_path.name}")
    log.debug(f"Texto ({len(text)} caracteres): {text[:100]}...")

    try:
        # Piper lee el texto desde stdin
        result = subprocess.run(
            cmd,
            input=text,
            capture_output=True,
            text=True,
            timeout=300,  # 5 min max
            cwd=str(piper_exe.parent),  # Necesario para DLLs de Piper
        )

        if result.returncode == 0 and output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            log.info(f"Audio generado: {output_path.name} ({size_mb:.2f} MB)")
            return output_path
        else:
            log.error(f"Piper falló (código {result.returncode})")
            if result.stderr:
                log.error(f"stderr: {result.stderr[:500]}")
            return None

    except subprocess.TimeoutExpired:
        log.error("Piper: timeout al generar audio (>5 min)")
        return None
    except FileNotFoundError:
        log.error(f"No se puede ejecutar Piper: {piper_exe}")
        return None
    except Exception as e:
        log.error(f"Error inesperado en TTS: {e}")
        return None


def generate_audio_from_script(
    script_path: Path,
    output_path: Optional[Path] = None,
) -> Optional[Path]:
    """
    Genera audio a partir de un archivo de guion Markdown.
    Lee el archivo, limpia el formato Markdown, y genera el audio.
    
    Args:
        script_path: Ruta del archivo de guion (.md).
        output_path: Ruta de salida. Si es None, se genera automáticamente.
    
    Returns:
        Ruta del archivo de audio, o None si falla.
    """
    if not script_path.exists():
        log.error(f"Guion no encontrado: {script_path}")
        return None

    text = script_path.read_text(encoding="utf-8")

    # Limpiar formato Markdown para TTS
    text = _clean_text_for_tts(text)

    if not text.strip():
        log.warning("Guion vacío después de limpieza")
        return None

    if output_path is None:
        output_path = script_path.parent / f"{script_path.stem}.wav"

    return generate_audio(text, output_path)


def _clean_text_for_tts(text: str) -> str:
    """
    Limpia texto Markdown para que sea leíble por TTS.
    Remueve frontmatter YAML, encabezados, bullets, etc.
    """
    import re

    lines = text.split("\n")
    cleaned = []
    in_frontmatter = False

    for line in lines:
        # Saltar frontmatter YAML
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue

        # Remover encabezados Markdown (mantener texto)
        line = re.sub(r"^#{1,6}\s+", "", line)

        # Remover negrita y cursiva (mantener texto)
        line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
        line = re.sub(r"\*(.+?)\*", r"\1", line)
        line = re.sub(r"__(.+?)__", r"\1", line)

        # Remover links Markdown
        line = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", line)

        # Remover bullets y checkboxes
        line = re.sub(r"^\s*[-*+]\s+(\[.\]\s+)?", "", line)
        line = re.sub(r"^\s*\d+\.\s+", "", line)

        # Remover código inline
        line = re.sub(r"`(.+?)`", r"\1", line)

        # Remover líneas horizontales
        if re.match(r"^---+$|^===+$|^\*\*\*+$", line.strip()):
            continue

        # Remover comentarios HTML
        line = re.sub(r"<!--.*?-->", "", line)

        if line.strip():
            cleaned.append(line.strip())

    return "\n".join(cleaned)
