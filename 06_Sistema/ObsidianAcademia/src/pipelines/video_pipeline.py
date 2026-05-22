"""
ObsidianAcademia - Video Pipeline
Pipeline: video → extracción audio → transcripción → IA → productos → vault.
"""

from pathlib import Path
from typing import Optional

from src.ingestion.audio_extractor import extract_audio_from_video
from src.pipelines.audio_pipeline import process_audio
from src.utils.logger import get_logger

log = get_logger("video_pipeline")


def process_video(
    video_path: Path,
    output_dir: Optional[Path] = None,
    curso: str = "",
    curso_nombre: str = "",
    semana: int = 0,
    tipo: str = "",
    generate_tts: bool = True,
    keep_extracted_audio: bool = True,
) -> dict:
    """
    Pipeline completo para procesar un archivo de video.
    
    Flujo:
    1. Extraer audio del video con ffmpeg
    2. Delegar al audio pipeline (transcripción + IA + TTS)
    
    Args:
        video_path: Ruta del archivo de video.
        output_dir: Directorio de salida.
        curso: ID del curso.
        curso_nombre: Nombre del curso.
        semana: Número de semana.
        tipo: "Teoria" o "Practica".
        generate_tts: Si True, genera audio explicativo.
        keep_extracted_audio: Si True, conserva el audio extraído.
    
    Returns:
        Diccionario con resultados (igual que audio_pipeline).
    """
    log.info(f"=== Video Pipeline: {video_path.name} ===")

    if not video_path.exists():
        log.error(f"Video no encontrado: {video_path}")
        return {
            "status": "failed",
            "source": str(video_path),
            "outputs": {},
            "errors": ["Video no encontrado"],
        }

    # --- Paso 1: Extraer audio ---
    log.info("[1/2] Extrayendo audio del video...")
    audio_output = None
    if output_dir:
        audio_output = output_dir / f"{video_path.stem}_audio.wav"

    audio_path = extract_audio_from_video(video_path, audio_output)

    if audio_path is None:
        log.error("No se pudo extraer audio del video")
        return {
            "status": "failed",
            "source": str(video_path),
            "outputs": {},
            "errors": ["Extracción de audio fallida"],
        }

    # --- Paso 2: Procesar como audio ---
    log.info("[2/2] Procesando audio extraído...")
    results = process_audio(
        audio_path=audio_path,
        output_dir=output_dir,
        curso=curso,
        curso_nombre=curso_nombre,
        semana=semana,
        tipo=tipo,
        generate_tts=generate_tts,
    )

    # Actualizar fuente original
    results["source"] = str(video_path)
    results["outputs"]["extracted_audio"] = str(audio_path)

    # Limpiar audio temporal si no se quiere conservar
    if not keep_extracted_audio and audio_path.exists():
        try:
            audio_path.unlink()
            log.debug("Audio temporal eliminado")
        except Exception:
            pass

    return results
