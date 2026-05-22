"""
ObsidianAcademia - Session Pipeline
Pipeline maestro: procesa todos los archivos de una sesión universitaria completa.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.config.constants import FileType
from src.config.settings import get_settings
from src.extraction.pdf_extractor import extract_text_from_pdf
from src.ingestion.audio_extractor import extract_audio_from_video
from src.ingestion.detector import classify_files
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
from src.utils.paths import build_session_path, ensure_dir

log = get_logger("session_pipeline")


def process_session(
    input_files: List[Path],
    curso: str,
    curso_nombre: str,
    semana: int,
    tipo: str,
    fecha: Optional[str] = None,
    generate_tts: bool = True,
    note_content: Optional[str] = None,
) -> dict:
    """
    Pipeline maestro para una sesión universitaria completa.
    Procesa todos los archivos de entrada y genera todos los productos.
    
    Flujo:
    1. Clasificar archivos de entrada
    2. Extraer audio de videos
    3. Transcribir audios
    4. Extraer texto de PDFs
    5. Consolidar todo el contenido
    6. Generar productos IA
    7. Generar audio TTS
    8. Guardar todo al vault
    
    Args:
        input_files: Lista de archivos de entrada.
        curso: ID del curso.
        curso_nombre: Nombre del curso.
        semana: Número de semana (1-16).
        tipo: "Teoria" o "Practica".
        fecha: Fecha de la sesión.
        generate_tts: Si True, genera audio explicativo.
        note_content: Contenido de notas Markdown adicional.
    
    Returns:
        Diccionario con resultados completos.
    """
    if not fecha:
        fecha = datetime.now().strftime("%Y-%m-%d")

    settings = get_settings()
    output_dir = build_session_path(settings.vault_path, curso, semana, tipo)
    ensure_dir(output_dir)

    results = {
        "status": "started",
        "curso": curso,
        "semana": semana,
        "tipo": tipo,
        "fecha": fecha,
        "source_files": [str(f) for f in input_files],
        "outputs": {},
        "errors": [],
        "content_parts": [],
    }

    log.info("=" * 60)
    log.info(f"SESIÓN: {curso_nombre} — Semana {semana} — {tipo}")
    log.info(f"Archivos de entrada: {len(input_files)}")
    log.info("=" * 60)

    # --- Paso 1: Clasificar archivos ---
    log.info("[1/7] Clasificando archivos...")
    classified = classify_files(input_files)
    content_parts = []

    # --- Paso 2: Extraer audio de videos ---
    videos = classified.get(FileType.VIDEO, [])
    extracted_audios = []
    if videos:
        log.info(f"[2/7] Extrayendo audio de {len(videos)} video(s)...")
        for video_path in videos:
            audio = extract_audio_from_video(
                video_path,
                output_dir / f"{video_path.stem}_audio.wav",
            )
            if audio:
                extracted_audios.append(audio)
                results["outputs"][f"extracted_audio_{video_path.stem}"] = str(audio)
            else:
                results["errors"].append(f"Fallo al extraer audio: {video_path.name}")
    else:
        log.info("[2/7] Sin videos — omitido")

    # --- Paso 3: Transcribir audios ---
    all_audios = classified.get(FileType.AUDIO, []) + extracted_audios
    if all_audios:
        log.info(f"[3/7] Transcribiendo {len(all_audios)} audio(s)...")
        for i, audio_path in enumerate(all_audios):
            transcript = transcribe_audio(audio_path)
            if transcript:
                # Guardar transcript individual
                suffix = f"_{i+1}" if len(all_audios) > 1 else ""
                saved = save_transcript(
                    transcript, output_dir, f"transcript{suffix}"
                )
                results["outputs"][f"transcript{suffix}"] = str(
                    saved.get("markdown", "")
                )
                content_parts.append(
                    f"## Transcripción: {audio_path.name}\n\n{transcript['text']}"
                )
            else:
                results["errors"].append(f"Fallo transcripción: {audio_path.name}")
    else:
        log.info("[3/7] Sin audios — omitido")

    # --- Paso 4: Extraer texto de PDFs ---
    pdfs = classified.get(FileType.PDF, [])
    if pdfs:
        log.info(f"[4/7] Extrayendo texto de {len(pdfs)} PDF(s)...")
        for pdf_path in pdfs:
            text = extract_text_from_pdf(pdf_path)
            if text:
                content_parts.append(
                    f"## Material PDF: {pdf_path.name}\n\n{text}"
                )
    else:
        log.info("[4/7] Sin PDFs — omitido")

    # --- Paso 4b: Notas Markdown ---
    markdowns = classified.get(FileType.MARKDOWN, [])
    if markdowns:
        log.info(f"Procesando {len(markdowns)} nota(s) Markdown...")
        for md_path in markdowns:
            try:
                md_text = md_path.read_text(encoding="utf-8")
                content_parts.append(
                    f"## Notas: {md_path.name}\n\n{md_text}"
                )
            except Exception as e:
                log.warning(f"Error al leer {md_path.name}: {e}")

    # Añadir nota de contenido adicional
    if note_content:
        content_parts.append(f"## Notas adicionales\n\n{note_content}")

    # --- Paso 5: Consolidar contenido ---
    log.info("[5/7] Consolidando contenido...")
    consolidated = "\n\n---\n\n".join(content_parts)

    if not consolidated.strip():
        results["status"] = "failed"
        results["errors"].append("No hay contenido consolidado para procesar")
        log.error("Sin contenido para generar productos IA")
        _save_metadata(results, output_dir)
        return results

    log.info(f"Contenido consolidado: {len(consolidated)} caracteres")

    # --- Paso 6: Generar productos IA ---
    log.info("[6/7] Generando productos con IA...")
    ai_products = generar_todos(
        contenido=consolidated,
        curso=curso_nombre,
        semana=str(semana),
        tipo=tipo,
        fecha=fecha,
    )

    # Guardar productos
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
            frontmatter = build_frontmatter({
                "tipo": product_key,
                "curso": curso,
                "curso_nombre": curso_nombre,
                "semana": semana,
                "sesion": tipo,
                "fecha": fecha,
                "estado": "completado",
                "tags": ["academia", product_key, curso],
            })

            file_path = output_dir / filename
            written = writer.write_note_absolute(
                file_path, f"{frontmatter}\n\n{content}", overwrite=True
            )
            if written:
                results["outputs"][product_key] = str(written)

    # --- Paso 7: Generar audio TTS ---
    if generate_tts and ai_products.get("guion_audio"):
        log.info("[7/7] Generando audio explicativo...")
        tts_path = output_dir / "audio_explicativo.wav"
        audio_result = generate_audio(ai_products["guion_audio"], tts_path)
        if audio_result:
            results["outputs"]["audio_tts"] = str(audio_result)
        else:
            results["errors"].append("Audio TTS falló")
    else:
        log.info("[7/7] Audio TTS omitido")

    # Crear nota de sesión principal
    _create_session_note(output_dir, results, writer, curso, curso_nombre, semana, tipo, fecha)

    # Metadata
    _save_metadata(results, output_dir)

    results["status"] = "completed" if not results["errors"] else "partial"
    log.info("=" * 60)
    log.info(f"SESIÓN COMPLETADA: {results['status']}")
    log.info(f"Productos generados: {len(results['outputs'])}")
    if results["errors"]:
        log.warning(f"Errores: {len(results['errors'])}")
    log.info("=" * 60)

    return results


def _create_session_note(
    output_dir: Path,
    results: dict,
    writer,
    curso: str,
    curso_nombre: str,
    semana: int,
    tipo: str,
    fecha: str,
):
    """Crea la nota principal de la sesión con links a todos los productos."""
    frontmatter = build_frontmatter({
        "id": f"{curso}_S{semana:02d}_{tipo}",
        "tipo": "sesion",
        "curso": curso,
        "curso_nombre": curso_nombre,
        "semana": semana,
        "sesion": tipo,
        "fecha": fecha,
        "estado": results.get("status", "en_proceso"),
        "tags": ["academia", "sesion", curso, tipo.lower()],
    })

    # Construir links a productos
    links_section = "## Productos generados\n\n"
    product_labels = {
        "transcript": "📝 Transcripción",
        "resumen": "📋 Resumen",
        "cuestionario": "❓ Cuestionario",
        "informe": "📊 Informe de sesión",
        "puntos_clave": "🎯 Puntos clave",
        "dudas": "❗ Dudas pendientes",
        "proximas_acciones": "✅ Próximas acciones",
        "guion_audio": "🎙️ Guion de audio",
        "audio_tts": "🔊 Audio explicativo",
    }

    for key, label in product_labels.items():
        if key in results.get("outputs", {}):
            path = Path(results["outputs"][key])
            links_section += f"- {label}: [[{path.name}]]\n"

    content = f"""{frontmatter}

# {curso_nombre} — Semana {semana} — {tipo}

**Fecha:** {fecha}

{links_section}

## Notas de clase

*Escribe aquí tus notas adicionales durante la clase...*

"""

    session_path = output_dir / "sesion.md"
    writer.write_note_absolute(session_path, content, overwrite=True)
    results["outputs"]["session_note"] = str(session_path)


def _save_metadata(results: dict, output_dir: Path):
    """Guarda metadata del procesamiento."""
    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    results["outputs"]["metadata"] = str(metadata_path)
