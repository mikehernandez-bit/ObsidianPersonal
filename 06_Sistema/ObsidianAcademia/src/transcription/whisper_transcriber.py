"""
ObsidianAcademia - Transcriptor Whisper
Transcripción de audio con faster-whisper (local, sin cloud).
"""

import json
from pathlib import Path
from typing import Optional

from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.utils.paths import ensure_dir

log = get_logger("transcriber")

# Lazy loading del modelo para evitar cargar en memoria hasta que se necesite
_whisper_model = None


def _get_model():
    """Carga el modelo de faster-whisper (lazy loading)."""
    global _whisper_model

    if _whisper_model is not None:
        return _whisper_model

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        log.error(
            "faster-whisper no está instalado. "
            "Ejecuta: pip install faster-whisper"
        )
        return None

    settings = get_settings()

    log.info(
        f"Cargando modelo Whisper: {settings.whisper_model_size} "
        f"(device={settings.whisper_device}, compute={settings.whisper_compute_type})"
    )

    try:
        _whisper_model = WhisperModel(
            settings.whisper_model_size,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )
        log.info("Modelo Whisper cargado correctamente")
        return _whisper_model
    except Exception as e:
        log.error(f"Error al cargar modelo Whisper: {e}")
        return None


def transcribe_audio(
    audio_path: Path,
    language: Optional[str] = None,
    timestamps: Optional[bool] = None,
) -> Optional[dict]:
    """
    Transcribe un archivo de audio usando faster-whisper.
    
    Args:
        audio_path: Ruta del archivo de audio.
        language: Código de idioma (ej: "es"). None para autodetección.
        timestamps: Si True, incluye timestamps por segmento.
    
    Returns:
        Diccionario con la transcripción:
        {
            "text": str,              # Texto completo
            "segments": [             # Lista de segmentos con timestamps
                {"start": float, "end": float, "text": str}
            ],
            "language": str,          # Idioma detectado
            "duration": float,        # Duración en segundos
            "source_file": str,       # Nombre del archivo fuente
        }
        Retorna None si falla.
    """
    model = _get_model()
    if model is None:
        return None

    if not audio_path.exists():
        log.error(f"Audio no encontrado: {audio_path}")
        return None

    settings = get_settings()
    if language is None:
        language = settings.whisper_language
    if timestamps is None:
        timestamps = settings.whisper_timestamps

    log.info(f"Transcribiendo: {audio_path.name} (idioma={language or 'auto'})")

    try:
        segments_iter, info = model.transcribe(
            str(audio_path),
            language=language if language else None,
            beam_size=settings.whisper_beam_size,
            word_timestamps=False,
            vad_filter=True,  # Filtro de actividad de voz para mejor calidad
        )

        # Recopilar segmentos
        segments = []
        full_text_parts = []

        for segment in segments_iter:
            seg_data = {
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip(),
            }
            segments.append(seg_data)
            full_text_parts.append(segment.text.strip())

        full_text = " ".join(full_text_parts)

        result = {
            "text": full_text,
            "segments": segments,
            "language": info.language,
            "language_probability": round(info.language_probability, 2),
            "duration": round(info.duration, 2),
            "source_file": audio_path.name,
        }

        log.info(
            f"Transcripción completada: {len(segments)} segmentos, "
            f"{info.duration:.0f}s, idioma={info.language} "
            f"(prob={info.language_probability:.0%})"
        )

        return result

    except Exception as e:
        log.error(f"Error en transcripción: {e}")
        return None


def format_transcript_markdown(
    transcript: dict,
    include_timestamps: bool = True,
) -> str:
    """
    Formatea una transcripción como Markdown.
    
    Args:
        transcript: Diccionario de transcripción (de transcribe_audio).
        include_timestamps: Si True, incluye timestamps por segmento.
    
    Returns:
        Texto Markdown formateado.
    """
    lines = []
    lines.append(f"# Transcripción: {transcript.get('source_file', 'audio')}\n")
    lines.append(f"- **Idioma:** {transcript.get('language', 'desconocido')}")
    lines.append(f"- **Duración:** {_format_duration(transcript.get('duration', 0))}")
    lines.append(f"- **Segmentos:** {len(transcript.get('segments', []))}")
    lines.append("")

    if include_timestamps and transcript.get("segments"):
        lines.append("## Transcripción con timestamps\n")
        for seg in transcript["segments"]:
            start = _format_timestamp(seg["start"])
            end = _format_timestamp(seg["end"])
            lines.append(f"**[{start} → {end}]** {seg['text']}\n")
    else:
        lines.append("## Texto completo\n")
        lines.append(transcript.get("text", ""))

    return "\n".join(lines)


def save_transcript(
    transcript: dict,
    output_dir: Path,
    filename: str = "transcript",
    save_json: bool = True,
    save_markdown: bool = True,
) -> dict:
    """
    Guarda la transcripción en archivo(s).
    
    Args:
        transcript: Diccionario de transcripción.
        output_dir: Directorio de salida.
        filename: Nombre base del archivo (sin extensión).
        save_json: Si True, guarda formato JSON.
        save_markdown: Si True, guarda formato Markdown.
    
    Returns:
        Diccionario con rutas de archivos guardados.
    """
    ensure_dir(output_dir)
    saved = {}

    if save_markdown:
        md_path = output_dir / f"{filename}.md"
        md_content = format_transcript_markdown(transcript)
        md_path.write_text(md_content, encoding="utf-8")
        saved["markdown"] = md_path
        log.info(f"Transcript MD guardado: {md_path}")

    if save_json:
        json_path = output_dir / f"{filename}.json"
        json_path.write_text(
            json.dumps(transcript, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        saved["json"] = json_path
        log.debug(f"Transcript JSON guardado: {json_path}")

    return saved


def _format_timestamp(seconds: float) -> str:
    """Formatea segundos como HH:MM:SS o MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def _format_duration(seconds: float) -> str:
    """Formatea duración como texto legible."""
    if seconds < 60:
        return f"{seconds:.0f} segundos"
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.1f} minutos"
    hours = minutes / 60
    return f"{hours:.1f} horas"
