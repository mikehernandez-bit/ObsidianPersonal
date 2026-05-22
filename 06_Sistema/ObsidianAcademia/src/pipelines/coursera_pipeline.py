"""
ObsidianAcademia - Coursera Pipeline
Pipeline para procesar material de Coursera: lecciones, módulos y cursos.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.config.settings import get_settings
from src.extraction.ocr_extractor import extract_text_from_image
from src.extraction.pdf_extractor import extract_text_from_pdf
from src.ingestion.audio_extractor import extract_audio_from_video
from src.ingestion.detector import classify_files, detect_file_type
from src.config.constants import FileType
from src.llm.generators import (
    generar_cuestionario,
    generar_descripcion_imagen,
    generar_guion_audio,
    generar_resumen,
)
from src.obsidian.template_renderer import build_frontmatter
from src.obsidian.writer_factory import get_writer
from src.transcription.whisper_transcriber import save_transcript, transcribe_audio
from src.tts.piper_tts import generate_audio
from src.utils.logger import get_logger
from src.utils.paths import build_coursera_path, ensure_dir

log = get_logger("coursera_pipeline")


def _describe_image_content(
    image_path: Path,
    course_name: str,
    module_name: str,
    lesson_name: str,
) -> str:
    """Describe una imagen usando vision real y cae a OCR si falla."""
    tema = f"{module_name} / {lesson_name}".strip(" /")
    vision_description = generar_descripcion_imagen(
        image_path=image_path,
        curso=course_name,
        tema=tema,
    )
    if vision_description:
        return "\n".join(
            [
                f"## Imagen: {image_path.name}",
                f"![[{image_path.name}]]",
                "",
                "### Analisis visual con Gemma 4",
                vision_description.strip(),
            ]
        )

    ocr_text = extract_text_from_image(image_path)
    if ocr_text:
        return "\n".join(
            [
                f"## Imagen: {image_path.name}",
                f"![[{image_path.name}]]",
                "",
                "### Fallback OCR",
                ocr_text.strip(),
            ]
        )

    return ""


def process_coursera_lesson(
    input_files: List[Path],
    course_name: str,
    module_name: str,
    lesson_name: str,
    program_name: Optional[str] = None,
    generate_tts: bool = True,
    note_content: Optional[str] = None,
) -> dict:
    """
    Procesa una lección de Coursera.
    
    Args:
        input_files: Archivos de entrada (video, PDF, notas).
        course_name: Nombre del curso de Coursera.
        module_name: Nombre del módulo.
        lesson_name: Nombre de la lección.
        program_name: Nombre del programa (None si es curso individual).
        generate_tts: Si True, genera audio explicativo.
        note_content: Notas adicionales en texto.
    
    Returns:
        Diccionario con resultados.
    """
    settings = get_settings()
    output_dir = build_coursera_path(
        settings.vault_path, program_name, course_name, module_name, lesson_name
    )
    ensure_dir(output_dir)

    results = {
        "status": "started",
        "type": "coursera_lesson",
        "program": program_name,
        "course": course_name,
        "module": module_name,
        "lesson": lesson_name,
        "outputs": {},
        "errors": [],
    }

    fecha = datetime.now().strftime("%Y-%m-%d")
    log.info(f"=== Coursera: {course_name} / {module_name} / {lesson_name} ===")

    # Clasificar archivos
    classified = classify_files(input_files)
    content_parts = []

    # Procesar videos → audio → transcripción
    videos = classified.get(FileType.VIDEO, [])
    audios = classified.get(FileType.AUDIO, [])

    for video_path in videos:
        audio = extract_audio_from_video(
            video_path, output_dir / f"{video_path.stem}_audio.wav"
        )
        if audio:
            audios.append(audio)

    for audio_path in audios:
        transcript = transcribe_audio(audio_path)
        if transcript:
            saved = save_transcript(transcript, output_dir, "transcript")
            results["outputs"]["transcript"] = str(saved.get("markdown", ""))
            content_parts.append(transcript["text"])

    # Procesar PDFs
    for pdf_path in classified.get(FileType.PDF, []):
        text = extract_text_from_pdf(pdf_path)
        if text:
            content_parts.append(text)

    # Procesar imagenes con vision real
    for image_path in classified.get(FileType.IMAGE, []):
        description = _describe_image_content(
            image_path=image_path,
            course_name=course_name,
            module_name=module_name,
            lesson_name=lesson_name,
        )
        if description:
            content_parts.append(description)

    # Notas markdown
    for md_path in classified.get(FileType.MARKDOWN, []):
        try:
            content_parts.append(md_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    if note_content:
        content_parts.append(note_content)

    # Consolidar
    consolidated = "\n\n".join(content_parts)

    if not consolidated.strip():
        results["status"] = "failed"
        results["errors"].append("Sin contenido para procesar")
        return results

    # Generar productos IA
    writer = get_writer()
    context = f"{course_name} - {module_name} - {lesson_name}"

    # Resumen
    resumen = generar_resumen(consolidated, context)
    if resumen:
        frontmatter = build_frontmatter({
            "tipo": "resumen",
            "plataforma": "coursera",
            "curso": course_name,
            "modulo": module_name,
            "leccion": lesson_name,
            "fecha": fecha,
            "tags": ["coursera", "resumen", course_name],
        })
        path = output_dir / "resumen.md"
        writer.write_note_absolute(path, f"{frontmatter}\n\n{resumen}", overwrite=True)
        results["outputs"]["resumen"] = str(path)

    # Cuestionario
    quiz = generar_cuestionario(consolidated, curso=context)
    if quiz:
        frontmatter = build_frontmatter({
            "tipo": "cuestionario",
            "plataforma": "coursera",
            "curso": course_name,
            "modulo": module_name,
            "leccion": lesson_name,
            "fecha": fecha,
            "tags": ["coursera", "cuestionario", course_name],
        })
        path = output_dir / "cuestionario.md"
        writer.write_note_absolute(path, f"{frontmatter}\n\n{quiz}", overwrite=True)
        results["outputs"]["cuestionario"] = str(path)

    # Guion audio + TTS
    guion = generar_guion_audio(consolidated, context, lesson_name)
    if guion:
        frontmatter = build_frontmatter({
            "tipo": "audio_script",
            "plataforma": "coursera",
            "curso": course_name,
            "modulo": module_name,
            "leccion": lesson_name,
            "fecha": fecha,
            "tags": ["coursera", "audio_script", course_name],
        })
        path = output_dir / "audio_script.md"
        writer.write_note_absolute(path, f"{frontmatter}\n\n{guion}", overwrite=True)
        results["outputs"]["guion_audio"] = str(path)

        if generate_tts:
            tts_path = output_dir / "audio_explicativo.wav"
            audio_result = generate_audio(guion, tts_path)
            if audio_result:
                results["outputs"]["audio_tts"] = str(audio_result)

    # Crear nota principal de lección
    _create_lesson_note(
        output_dir, results, writer, course_name, module_name,
        lesson_name, program_name, fecha,
    )

    # Metadata
    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    results["status"] = "completed" if not results["errors"] else "partial"
    log.info(f"=== Lección Coursera completada: {results['status']} ===")
    return results


def _create_lesson_note(
    output_dir, results, writer, course_name, module_name,
    lesson_name, program_name, fecha,
):
    """Crea la nota principal de la lección."""
    frontmatter = build_frontmatter({
        "tipo": "leccion_coursera",
        "plataforma": "coursera",
        "programa": program_name or "",
        "curso": course_name,
        "modulo": module_name,
        "leccion": lesson_name,
        "fecha": fecha,
        "estado": "completado",
        "tags": ["coursera", "leccion", course_name],
    })

    links = "## Productos\n\n"
    labels = {
        "transcript": "📝 Transcripción",
        "resumen": "📋 Resumen",
        "cuestionario": "❓ Cuestionario",
        "guion_audio": "🎙️ Guion de audio",
        "audio_tts": "🔊 Audio explicativo",
    }
    for key, label in labels.items():
        if key in results.get("outputs", {}):
            path = Path(results["outputs"][key])
            links += f"- {label}: [[{path.name}]]\n"

    content = f"""{frontmatter}

# {lesson_name}

**Curso:** {course_name}
**Módulo:** {module_name}
{f"**Programa:** {program_name}" if program_name else ""}
**Fecha:** {fecha}

{links}

## Notas

*Escribe aquí tus notas de la lección...*
"""

    path = output_dir / "leccion.md"
    writer.write_note_absolute(path, content, overwrite=True)
    results["outputs"]["lesson_note"] = str(path)
