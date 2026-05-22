"""
ObsidianAcademia - Extractor de Audio
Extrae audio de archivos de video usando ffmpeg.
"""

import subprocess
from pathlib import Path
from typing import Optional

from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.utils.paths import ensure_dir

log = get_logger("audio_extractor")


def extract_audio_from_video(
    video_path: Path,
    output_path: Optional[Path] = None,
    sample_rate: int = 16000,
    channels: int = 1,
) -> Optional[Path]:
    """
    Extrae el audio de un archivo de video usando ffmpeg.
    Genera un archivo WAV optimizado para transcripción (16kHz mono).
    
    Args:
        video_path: Ruta del archivo de video.
        output_path: Ruta de salida para el audio WAV. 
                      Si es None, se genera automáticamente.
        sample_rate: Frecuencia de muestreo (defecto: 16000 Hz).
        channels: Número de canales (defecto: 1 = mono).
    
    Returns:
        Ruta del archivo de audio extraído, o None si falla.
    """
    settings = get_settings()
    ffmpeg_exe = settings.ffmpeg_exe

    if not ffmpeg_exe.exists():
        log.error(f"ffmpeg no encontrado: {ffmpeg_exe}")
        log.info(
            "Ejecuta install.ps1 para descargar ffmpeg o configura la ruta en config.yaml"
        )
        return None

    if not video_path.exists():
        log.error(f"Video no encontrado: {video_path}")
        return None

    # Generar ruta de salida si no se especificó
    if output_path is None:
        output_dir = settings.output_transcripts
        ensure_dir(output_dir)
        output_path = output_dir / f"{video_path.stem}_audio.wav"

    ensure_dir(output_path.parent)

    # Construir comando ffmpeg
    cmd = [
        str(ffmpeg_exe),
        "-i", str(video_path),       # Entrada
        "-vn",                        # Sin video
        "-acodec", "pcm_s16le",       # Codec WAV 16-bit
        "-ar", str(sample_rate),      # Sample rate
        "-ac", str(channels),         # Canales
        "-y",                         # Sobreescribir si existe
        str(output_path),             # Salida
    ]

    log.info(f"Extrayendo audio de: {video_path.name}")
    log.debug(f"Comando: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutos max
        )

        if result.returncode == 0:
            size_mb = output_path.stat().st_size / (1024 * 1024)
            log.info(f"Audio extraído: {output_path.name} ({size_mb:.1f} MB)")
            return output_path
        else:
            log.error(f"ffmpeg falló (código {result.returncode})")
            log.error(f"stderr: {result.stderr[:500]}")
            return None

    except subprocess.TimeoutExpired:
        log.error("ffmpeg: timeout al extraer audio (>10 min)")
        return None
    except FileNotFoundError:
        log.error(f"No se puede ejecutar ffmpeg: {ffmpeg_exe}")
        return None
    except Exception as e:
        log.error(f"Error inesperado al extraer audio: {e}")
        return None


def get_media_duration(file_path: Path) -> Optional[float]:
    """
    Obtiene la duración de un archivo de audio/video en segundos usando ffprobe.
    
    Args:
        file_path: Ruta del archivo multimedia.
    
    Returns:
        Duración en segundos, o None si no se puede determinar.
    """
    settings = get_settings()
    ffprobe_exe = settings.ffprobe_exe

    if not ffprobe_exe.exists():
        log.warning("ffprobe no disponible, no se puede obtener duración")
        return None

    cmd = [
        str(ffprobe_exe),
        "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
        pass

    return None


def convert_audio_format(
    input_path: Path,
    output_path: Path,
    sample_rate: int = 16000,
    channels: int = 1,
) -> Optional[Path]:
    """
    Convierte un archivo de audio a formato WAV óptimo para transcripción.
    Útil cuando el audio de entrada no es WAV 16kHz mono.
    
    Args:
        input_path: Ruta del audio de entrada.
        output_path: Ruta de salida WAV.
        sample_rate: Frecuencia de muestreo.
        channels: Número de canales.
    
    Returns:
        Ruta del archivo convertido, o None si falla.
    """
    settings = get_settings()
    ffmpeg_exe = settings.ffmpeg_exe

    if not ffmpeg_exe.exists():
        log.error(f"ffmpeg no encontrado: {ffmpeg_exe}")
        return None

    ensure_dir(output_path.parent)

    cmd = [
        str(ffmpeg_exe),
        "-i", str(input_path),
        "-acodec", "pcm_s16le",
        "-ar", str(sample_rate),
        "-ac", str(channels),
        "-y",
        str(output_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            log.info(f"Audio convertido: {output_path.name}")
            return output_path
        else:
            log.error(f"Error al convertir audio: {result.stderr[:300]}")
            return None
    except Exception as e:
        log.error(f"Error al convertir audio: {e}")
        return None
