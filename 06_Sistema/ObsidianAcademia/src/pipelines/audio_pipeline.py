"""
ObsidianAcademia - Audio Pipeline
Pipeline: audio → transcripción → IA → productos → vault.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config.settings import get_settings
from src.ingestion.audio_extractor import get_media_duration
from src.llm.generators import generar_todos
from src.obsidian.template_renderer import build_frontmatter
from src.obsidian.writer_factory import get_writer
from src.transcription.whisper_transcriber import (
    format_transcript_markdown,
    save_transcript,
    transcribe_audio,
)
from src.tts.piper_tts import generate_audio
from src.utils.logger import get_logger
from src.utils.paths import ensure_dir

log = get_logger("audio_pipeline")


def process_audio(
    audio_path: Path,
    output_dir: Optional[Path] = None,
    curso: str = "",
    curso_nombre: str = "",
    semana: int = 0,
    tipo: str = "",
    generate_tts: bool = True,
) -> dict:
    """
    Pipeline completo para procesar un archivo de audio.
    
    Flujo:
    1. Transcribir audio con faster-whisper
    2. Generar productos IA (resumen, quiz, etc.)
    3. Generar audio TTS del guion
    4. Guardar todo al vault
    
    Args:
        audio_path: Ruta del archivo de audio.
        output_dir: Directorio de salida. Si None, se determina automáticamente.
        curso: ID del curso.
        curso_nombre: Nombre del curso.
        semana: Número de semana.
        tipo: "Teoria" o "Practica".
        generate_tts: Si True, genera audio explicativo.
    
    Returns:
        Diccionario con rutas de todos los archivos generados y estado.
    """
    results = {
        "status": "started",
        "source": str(audio_path),
        "outputs": {},
        "errors": [],
    }

    settings = get_settings()

    # Determinar directorio de salida
    if output_dir is None:
        if curso and semana and tipo:
            from src.utils.paths import build_session_path
            output_dir = build_session_path(
                settings.vault_path, curso, semana, tipo
            )
        else:
            output_dir = settings.output_transcripts / audio_path.stem

    ensure_dir(output_dir)
    log.info(f"=== Audio Pipeline: {audio_path.name} ===")

    # --- Paso 1: Transcripción ---
    log.info("[1/4] Transcribiendo audio...")
    transcript = transcribe_audio(audio_path)

    if transcript is None:
        results["errors"].append("Transcripción falló")
        results["status"] = "partial"
        log.error("Transcripción falló — continuando sin transcript")
        # Intentar continuar si hay contenido alternativo
        transcript_text = ""
    else:
        # Guardar transcripción
        saved = save_transcript(transcript, output_dir, "transcript")
        results["outputs"]["transcript_md"] = str(saved.get("markdown", ""))
        results["outputs"]["transcript_json"] = str(saved.get("json", ""))
        transcript_text = transcript.get("text", "")

    if not transcript_text:
        results["status"] = "failed"
        results["errors"].append("No hay contenido para procesar")
        log.error("Sin contenido para generar productos IA")
        return results

    # --- Paso 2: Generar productos IA ---
    log.info("[2/4] Generando productos con IA...")
    fecha = datetime.now().strftime("%Y-%m-%d")
    ai_products = generar_todos(
        contenido=transcript_text,
        curso=curso_nombre or curso,
        semana=str(semana) if semana else "",
        tipo=tipo,
        fecha=fecha,
    )

    # --- Paso 3: Guardar productos al vault ---
    log.info("[3/4] Guardando productos en el vault...")
    writer = get_writer()

    product_filenames = {
        "resumen": "resumen.md",
        "cuestionario": "cuestionario.md",
        "informe": "informe.md",
        "puntos_clave": "puntos_clave.md",
        "dudas": "dudas.md",
        "proximas_acciones": "proximas_acciones.md",
        "guion_audio": "audio_script.md",
    }

    for product_key, filename in product_filenames.items():
        content = ai_products.get(product_key)
        if content:
            # Añadir frontmatter
            frontmatter = build_frontmatter({
                "tipo": product_key,
                "curso": curso,
                "semana": semana,
                "sesion": tipo,
                "fecha": fecha,
                "fuente": audio_path.name,
                "estado": "completado",
                "tags": ["academia", product_key, curso],
            })

            full_content = f"{frontmatter}\n\n{content}"
            file_path = output_dir / filename

            written = writer.write_note_absolute(file_path, full_content, overwrite=True)
            if written:
                results["outputs"][product_key] = str(written)
            else:
                results["errors"].append(f"No se pudo guardar: {filename}")

    # --- Paso 4: Generar audio TTS ---
    if generate_tts and ai_products.get("guion_audio"):
        log.info("[4/4] Generando audio explicativo...")
        tts_path = output_dir / "audio_explicativo.wav"
        audio_result = generate_audio(ai_products["guion_audio"], tts_path)
        if audio_result:
            results["outputs"]["audio_tts"] = str(audio_result)
        else:
            results["errors"].append("Generación de audio TTS falló")
    else:
        log.info("[4/4] Audio TTS omitido")

    # --- Guardar metadata ---
    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    results["outputs"]["metadata"] = str(metadata_path)

    # Estado final
    if results["errors"]:
        results["status"] = "partial"
    else:
        results["status"] = "completed"

    log.info(f"=== Pipeline completado: {results['status']} ===")
    log.info(f"Productos generados: {len(results['outputs'])}")
    if results["errors"]:
        log.warning(f"Errores: {results['errors']}")

    return results
