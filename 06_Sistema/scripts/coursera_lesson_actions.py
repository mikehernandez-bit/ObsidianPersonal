from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SYSTEM_DIR = SCRIPT_DIR.parent
LOCAL_PROJECT_DIR = SYSTEM_DIR / "ObsidianAcademia"
LEGACY_PROJECT_DIR = Path(r"C:\Users\jhoan\ObsidianAcademia")
PROJECT_DIR = Path(
    os.environ.get(
        "OBSIDIAN_ACADEMIA_PROJECT_DIR",
        str(LOCAL_PROJECT_DIR if LOCAL_PROJECT_DIR.exists() else LEGACY_PROJECT_DIR),
    )
)
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from src.extraction.ocr_extractor import extract_text_from_image
from src.extraction.pdf_extractor import extract_text_from_pdf
from src.llm.generators import (
    generar_cuestionario,
    generar_descripcion_imagen,
    generar_guion_audio,
    generar_informe,
)
from src.obsidian.template_renderer import build_frontmatter
from src.pipelines.coursera_pipeline import process_coursera_lesson
from src.tts.piper_tts import generate_audio

GENERATED_FILES = {
    "transcript.md",
    "resumen.md",
    "informe.md",
    "cuestionario.md",
    "audio_script.md",
    "audio_explicativo.wav",
    "metadata.json",
    "leccion.md",
}
USER_NOTE_SECTIONS = {
    "Notas de la leccion",
    "Conceptos clave",
    "Ideas importantes",
    "Links y recursos mencionados",
    "Dudas",
    "Reflexion",
}
PDF_EXTENSIONS = {".pdf"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".opus"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
TEXT_EXTENSIONS = {".md"}
SUPPORTED_INPUT_EXTENSIONS = (
    PDF_EXTENSIONS | AUDIO_EXTENSIONS | VIDEO_EXTENSIONS | IMAGE_EXTENSIONS | TEXT_EXTENSIONS
)
IMAGE_ANALYSIS_CACHE: dict[tuple[str, int], tuple[str, str]] = {}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def strip_frontmatter(content: str) -> str:
    return re.sub(r"^---\s*\n.*?\n---\s*\n?", "", content, flags=re.DOTALL)


def split_frontmatter(content: str) -> tuple[str, str]:
    match = re.match(r"(?s)\A(---\n.*?\n---\n?)(.*)\Z", content)
    if match:
        return match.group(1), match.group(2).lstrip("\n")
    return "", content


def collect_input_files(lesson_dir: Path, note_path: Path) -> list[Path]:
    files: list[Path] = []

    for child in lesson_dir.iterdir():
        if not child.is_file():
            continue
        if child.resolve() == note_path.resolve():
            continue
        if child.name.lower() in GENERATED_FILES:
            continue
        if child.suffix.lower() not in SUPPORTED_INPUT_EXTENSIONS:
            continue
        files.append(child)

    return sorted(files)


def build_statuses(lesson_dir: Path) -> dict[str, str]:
    return {
        "transcript_status": "generado" if (lesson_dir / "transcript.md").exists() else "pendiente",
        "summary_status": "generado" if (lesson_dir / "resumen.md").exists() else "pendiente",
        "report_status": "generado" if (lesson_dir / "informe.md").exists() else "pendiente",
        "quiz_status": "generado" if (lesson_dir / "cuestionario.md").exists() else "pendiente",
        "audio_status": "generado" if (lesson_dir / "audio_explicativo.wav").exists() else "pendiente",
    }


def write_markdown(path: Path, frontmatter: dict[str, object], body: str) -> Path:
    content = f"{build_frontmatter(frontmatter)}\n\n{body.strip()}\n"
    path.write_text(content, encoding="utf-8")
    return path


def note_frontmatter(args: argparse.Namespace, tipo: str) -> dict[str, object]:
    return {
        "tipo": tipo,
        "plataforma": "coursera",
        "programa": args.program or "",
        "curso": args.course,
        "modulo": args.module,
        "leccion": args.lesson,
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "tags": ["coursera", tipo, args.course],
    }


def _image_cache_key(file_path: Path) -> tuple[str, int]:
    stat = file_path.stat()
    return (str(file_path.resolve()), int(stat.st_mtime_ns))


def describe_image_for_study(
    file_path: Path,
    args: argparse.Namespace,
) -> tuple[str, str]:
    cache_key = _image_cache_key(file_path)
    cached = IMAGE_ANALYSIS_CACHE.get(cache_key)
    if cached:
        return cached

    tema = " / ".join(part for part in [args.module, args.lesson] if part)
    vision_text = generar_descripcion_imagen(
        image_path=file_path,
        curso=args.course,
        tema=tema,
    )
    if vision_text and vision_text.strip():
        result = ("vision", vision_text.strip())
        IMAGE_ANALYSIS_CACHE[cache_key] = result
        return result

    ocr_text = extract_text_from_image(file_path)
    if ocr_text and ocr_text.strip():
        result = ("ocr", ocr_text.strip())
        IMAGE_ANALYSIS_CACHE[cache_key] = result
        return result

    result = ("empty", "No se pudo extraer contenido util de la imagen.")
    IMAGE_ANALYSIS_CACHE[cache_key] = result
    return result


def image_mode_heading(mode: str) -> str:
    if mode == "vision":
        return "### Analisis visual con Gemma 4"
    if mode == "ocr":
        return "### Fallback OCR"
    return "### Analisis no disponible"


def image_mode_label(mode: str) -> str:
    if mode == "vision":
        return "Descripcion con Gemma 4 Vision"
    if mode == "ocr":
        return "Descripcion base (OCR)"
    return "Sin descripcion util"


def collect_consolidated_content(args: argparse.Namespace) -> str:
    lesson_dir = Path(args.lesson_dir)
    note_path = Path(args.note)
    sections: list[str] = []

    if note_path.exists():
        note_text = extract_user_note_content(read_text(note_path)).strip()
        if note_text:
            sections.append(f"## Notas de la leccion\n\n{note_text}")

    transcript_path = lesson_dir / "transcript.md"
    if transcript_path.exists():
        transcript_text = strip_frontmatter(read_text(transcript_path)).strip()
        if transcript_text:
            sections.append(f"## Transcripcion disponible\n\n{transcript_text}")

    for file_path in collect_input_files(lesson_dir, note_path):
        suffix = file_path.suffix.lower()

        if suffix in PDF_EXTENSIONS:
            pdf_text = extract_text_from_pdf(file_path)
            if pdf_text:
                sections.append(f"## PDF: {file_path.name}\n\n{pdf_text}")
            continue

        if suffix in IMAGE_EXTENSIONS:
            mode, image_text = describe_image_for_study(file_path, args)
            sections.append(
                "\n".join(
                    [
                        f"## Imagen: {file_path.name}",
                        f"![[{file_path.name}]]",
                        "",
                        image_mode_heading(mode),
                        image_text,
                    ]
                )
            )
            continue

        if suffix in TEXT_EXTENSIONS:
            text = strip_frontmatter(read_text(file_path)).strip()
            if text:
                sections.append(f"## Nota adicional: {file_path.name}\n\n{text}")

    return "\n\n---\n\n".join(section for section in sections if section.strip())


def build_image_appendix(
    lesson_dir: Path,
    note_path: Path,
    args: argparse.Namespace,
) -> str:
    blocks: list[str] = []

    for file_path in collect_input_files(lesson_dir, note_path):
        if file_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        mode, image_text = describe_image_for_study(file_path, args)
        blocks.append(
            "\n".join(
                [
                    f"### {file_path.name}",
                    f"![[{file_path.name}]]",
                    "",
                    f"**{image_mode_label(mode)}:**",
                    image_text,
                ]
            )
        )

    return "\n\n".join(blocks)


def ensure_content(content: str, message: str) -> str:
    if not content.strip():
        raise RuntimeError(message)
    return content


def _iter_level_two_sections(body: str) -> list[tuple[str, str]]:
    pattern = re.compile(r"(?ms)^## (.+?)\n(.*?)(?=^## |\Z)")
    sections: list[tuple[str, str]] = []

    for match in pattern.finditer(body):
        title = match.group(1).strip()
        section_body = re.sub(r"\n*---\s*\Z", "", match.group(2)).strip()
        sections.append((title, section_body))

    return sections


def _cleanup_manual_section(section_body: str) -> str:
    cleaned_lines: list[str] = []

    for raw_line in section_body.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            cleaned_lines.append("")
            continue
        if re.fullmatch(r"### Punto \d+", stripped):
            continue
        if stripped in {"-", ">", "1.", "2.", "3.", "**Puntaje:** /"}:
            continue
        if re.fullmatch(r"\|[-| :]+\|", stripped):
            continue
        if re.fullmatch(r"\|(\s*\|\s*)+", stripped):
            continue
        cleaned_lines.append(raw_line.rstrip())

    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def extract_user_note_content(note_text: str) -> str:
    body = strip_frontmatter(note_text)
    sections: list[str] = []

    for title, section_body in _iter_level_two_sections(body):
        if title not in USER_NOTE_SECTIONS:
            continue
        cleaned = _cleanup_manual_section(section_body)
        if cleaned:
            sections.append(f"## {title}\n\n{cleaned}")

    return "\n\n---\n\n".join(sections)


def _format_wikilink_list(files: list[Path], empty_label: str = "Pendiente") -> str:
    if not files:
        return f"- {empty_label}"
    return "\n".join(f"- [[{file_path.name}]]" for file_path in files)


def _link_or_pending(path: Path) -> str:
    return f"[[{path.name}]]" if path.exists() else "pendiente"


def _replace_or_append_section(body: str, title: str, new_body: str) -> str:
    pattern = re.compile(rf"(?ms)^## {re.escape(title)}\n.*?(?=^## |\Z)")
    match = pattern.search(body)
    replacement = f"## {title}\n\n{new_body.strip()}\n\n"

    if match:
        if match.group(0).rstrip().endswith("---"):
            replacement += "---\n\n"
        return body[:match.start()] + replacement + body[match.end():]

    suffix = "" if body.endswith("\n") else "\n"
    return f"{body}{suffix}\n---\n\n{replacement}"


def render_materials_section(lesson_dir: Path, note_path: Path) -> str:
    source_files = collect_input_files(lesson_dir, note_path)
    pdfs = [path for path in source_files if path.suffix.lower() in PDF_EXTENSIONS]
    audios = [path for path in source_files if path.suffix.lower() in AUDIO_EXTENSIONS]
    videos = [path for path in source_files if path.suffix.lower() in VIDEO_EXTENSIONS]
    images = [path for path in source_files if path.suffix.lower() in IMAGE_EXTENSIONS]
    notes = [path for path in source_files if path.suffix.lower() in TEXT_EXTENSIONS]

    lines = [
        "> Esta carpeta de leccion es el contenedor de PDF, audio, video e imagenes.",
        "> Deja aqui el material y luego usa los botones del panel de IA.",
        "",
        "### PDF",
        "",
        _format_wikilink_list(pdfs, "Sin PDF"),
        "",
        "### Audio",
        "",
        _format_wikilink_list(audios, "Sin audio"),
        "",
        "### Video",
        "",
        _format_wikilink_list(videos, "Sin video"),
        "",
        "### Imagenes",
        "",
        _format_wikilink_list(images, "Sin imagenes"),
        "",
        "### Notas auxiliares",
        "",
        _format_wikilink_list(notes, "Sin notas auxiliares"),
    ]

    return "\n".join(lines)


def render_transcriptions_section(lesson_dir: Path, note_path: Path) -> str:
    source_files = collect_input_files(lesson_dir, note_path)
    audios = [path for path in source_files if path.suffix.lower() in AUDIO_EXTENSIONS]
    videos = [path for path in source_files if path.suffix.lower() in VIDEO_EXTENSIONS]
    transcript_path = lesson_dir / "transcript.md"

    lines = [
        "### Fuentes detectadas",
        "",
        f"- Audio: {', '.join(f'[[{path.name}]]' for path in audios) if audios else 'Sin audio fuente'}",
        f"- Video: {', '.join(f'[[{path.name}]]' for path in videos) if videos else 'Sin video fuente'}",
        "",
        "### Transcript consolidado",
        "",
    ]

    if transcript_path.exists():
        lines.extend(
            [
                f"- Archivo: [[{transcript_path.name}]]",
                "",
                f"![[{transcript_path.name}]]",
            ]
        )
    else:
        lines.append("> No hay transcript generado todavia.")

    return "\n".join(lines)


def render_report_section(lesson_dir: Path) -> str:
    report_path = lesson_dir / "informe.md"
    if not report_path.exists():
        return "> Este informe debe consolidar notas, transcripciones, imagenes y aclaraciones.\n>\n> Estado: pendiente."

    return "\n".join(
        [
            f"- Archivo principal: [[{report_path.name}]]",
            "",
            f"![[{report_path.name}]]",
        ]
    )


def render_products_section(lesson_dir: Path) -> str:
    statuses = build_statuses(lesson_dir)
    transcript_path = lesson_dir / "transcript.md"
    summary_path = lesson_dir / "resumen.md"
    report_path = lesson_dir / "informe.md"
    quiz_path = lesson_dir / "cuestionario.md"
    script_path = lesson_dir / "audio_script.md"
    audio_path = lesson_dir / "audio_explicativo.wav"

    lines = [
        "> [!info] Estado actual",
        f"> - Transcript: {statuses['transcript_status']}",
        f"> - Resumen: {statuses['summary_status']}",
        f"> - Informe: {statuses['report_status']}",
        f"> - Cuestionario: {statuses['quiz_status']}",
        f"> - Audio: {statuses['audio_status']}",
        "",
        "### Archivos disponibles",
        "",
        f"- Transcripcion: {_link_or_pending(transcript_path)}",
        f"- Resumen: {_link_or_pending(summary_path)}",
        f"- Informe: {_link_or_pending(report_path)}",
        f"- Cuestionario: {_link_or_pending(quiz_path)}",
        f"- Guion de audio: {_link_or_pending(script_path)}",
        f"- Audio explicativo: {_link_or_pending(audio_path)}",
    ]

    if audio_path.exists():
        lines.extend(
            [
                "",
                "### Reproductor",
                "",
                f"![[{audio_path.name}]]",
            ]
        )

    return "\n".join(lines)


def render_quiz_section(lesson_dir: Path) -> str:
    quiz_path = lesson_dir / "cuestionario.md"
    if not quiz_path.exists():
        return "> El cuestionario se mostrara aqui cuando exista `cuestionario.md`."

    return "\n".join(
        [
            f"- Archivo principal: [[{quiz_path.name}]]",
            "",
            f"![[{quiz_path.name}]]",
        ]
    )


def refresh_lesson_note(note_path: Path, lesson_dir: Path) -> None:
    if not note_path.exists():
        return

    frontmatter, body = split_frontmatter(read_text(note_path))
    updated_body = body
    updated_body = _replace_or_append_section(
        updated_body,
        "Materiales de la leccion",
        render_materials_section(lesson_dir, note_path),
    )
    updated_body = _replace_or_append_section(
        updated_body,
        "Transcripciones",
        render_transcriptions_section(lesson_dir, note_path),
    )
    updated_body = _replace_or_append_section(
        updated_body,
        "Informe maestro",
        render_report_section(lesson_dir),
    )
    updated_body = _replace_or_append_section(
        updated_body,
        "Productos generados",
        render_products_section(lesson_dir),
    )
    updated_body = _replace_or_append_section(
        updated_body,
        "Quiz de Coursera",
        render_quiz_section(lesson_dir),
    )

    note_path.write_text(f"{frontmatter}{updated_body.strip()}\n", encoding="utf-8")


def _copy_generated_file(source: Path, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target


def _cleanup_generated_tree(source_dir: Path, lesson_dir: Path) -> None:
    source_dir = source_dir.resolve()
    lesson_dir = lesson_dir.resolve()

    if source_dir == lesson_dir or not source_dir.exists():
        return

    children = list(source_dir.iterdir())
    if any(child.is_dir() for child in children):
        return

    if not all(child.name.lower() in GENERATED_FILES for child in children):
        return

    shutil.rmtree(source_dir)

    current = source_dir.parent
    coursera_root = lesson_dir.parents[3] if len(lesson_dir.parents) >= 4 else None
    while coursera_root and current != coursera_root and current.exists():
        if any(current.iterdir()):
            break
        current.rmdir()
        current = current.parent


def _sync_pipeline_outputs(results: dict[str, object], lesson_dir: Path, note_path: Path) -> None:
    outputs = results.get("outputs", {})
    if not isinstance(outputs, dict):
        return

    source_dirs: set[Path] = set()
    synced_outputs: dict[str, str] = {}

    for key, raw_path in outputs.items():
        if not raw_path:
            continue

        source_path = Path(raw_path)
        if not source_path.exists():
            continue

        source_dirs.add(source_path.parent)

        if key == "lesson_note":
            if source_path.resolve() != note_path.resolve():
                source_path.unlink(missing_ok=True)
            continue

        target_path = lesson_dir / source_path.name
        if source_path.resolve() != target_path.resolve():
            _copy_generated_file(source_path, target_path)
        synced_outputs[key] = str(target_path)

    for source_dir in source_dirs:
        metadata_path = source_dir / "metadata.json"
        if metadata_path.exists():
            _copy_generated_file(metadata_path, lesson_dir / "metadata.json")

    outputs.update(synced_outputs)

    for source_dir in source_dirs:
        _cleanup_generated_tree(source_dir, lesson_dir)


def action_process_full(args: argparse.Namespace) -> dict[str, object]:
    lesson_dir = Path(args.lesson_dir)
    note_path = Path(args.note)
    input_files = collect_input_files(lesson_dir, note_path)
    note_text = extract_user_note_content(read_text(note_path)) if note_path.exists() else ""

    results = process_coursera_lesson(
        input_files=input_files,
        course_name=args.course,
        module_name=args.module,
        lesson_name=args.lesson,
        program_name=args.program or None,
        generate_tts=True,
        note_content=note_text,
    )
    _sync_pipeline_outputs(results, lesson_dir, note_path)

    generated_note = lesson_dir / "leccion.md"
    if generated_note.exists() and generated_note.resolve() != note_path.resolve():
        generated_note.unlink()

    refresh_lesson_note(note_path, lesson_dir)

    open_file = None
    if (lesson_dir / "transcript.md").exists():
        open_file = str(lesson_dir / "transcript.md")
    elif (lesson_dir / "resumen.md").exists():
        open_file = str(lesson_dir / "resumen.md")

    return {
        "ok": results.get("status") in {"completed", "partial"},
        "message": "Leccion procesada. Se actualizaron transcript, resumen, cuestionario y audio cuando hubo material compatible.",
        "statuses": build_statuses(lesson_dir),
        "open_file": open_file,
    }


def action_generate_report(args: argparse.Namespace) -> dict[str, object]:
    lesson_dir = Path(args.lesson_dir)
    note_path = Path(args.note)
    content = ensure_content(
        collect_consolidated_content(args),
        "No hay contenido suficiente para generar el informe.",
    )
    report = generar_informe(
        contenido=content,
        curso=args.course,
        semana=args.module,
        tipo="Coursera",
        fecha=datetime.now().strftime("%Y-%m-%d"),
    )
    if not report:
        raise RuntimeError("No se pudo generar el informe con el modelo local.")

    image_appendix = build_image_appendix(lesson_dir, note_path, args)
    final_body = report.strip()
    if image_appendix:
        final_body += f"\n\n---\n\n## Imagenes analizadas\n\n{image_appendix}"

    report_path = write_markdown(
        lesson_dir / "informe.md",
        note_frontmatter(args, "informe"),
        final_body,
    )
    refresh_lesson_note(note_path, lesson_dir)

    return {
        "ok": True,
        "message": "Informe generado en la carpeta de la leccion.",
        "statuses": build_statuses(lesson_dir),
        "open_file": str(report_path),
    }


def action_generate_audio(args: argparse.Namespace) -> dict[str, object]:
    lesson_dir = Path(args.lesson_dir)
    report_path = lesson_dir / "informe.md"
    if report_path.exists():
        source_text = strip_frontmatter(read_text(report_path))
    else:
        source_text = collect_consolidated_content(args)

    source_text = ensure_content(
        source_text,
        "No hay contenido suficiente para generar audio.",
    )
    audio_script = generar_guion_audio(source_text, args.course, args.lesson)
    if not audio_script:
        raise RuntimeError("No se pudo generar el guion de audio.")

    script_path = write_markdown(
        lesson_dir / "audio_script.md",
        note_frontmatter(args, "audio_script"),
        audio_script,
    )
    audio_path = lesson_dir / "audio_explicativo.wav"
    generated_audio = generate_audio(audio_script, audio_path)
    if not generated_audio:
        raise RuntimeError("El guion se genero, pero fallo la creacion del audio explicativo.")

    refresh_lesson_note(Path(args.note), lesson_dir)

    return {
        "ok": True,
        "message": "Audio de estudio generado desde el informe o el contenido consolidado.",
        "statuses": build_statuses(lesson_dir),
        "open_file": str(script_path),
    }


def action_generate_quiz(args: argparse.Namespace) -> dict[str, object]:
    lesson_dir = Path(args.lesson_dir)
    report_path = lesson_dir / "informe.md"
    if report_path.exists():
        source_text = strip_frontmatter(read_text(report_path))
    else:
        source_text = collect_consolidated_content(args)

    source_text = ensure_content(
        source_text,
        "No hay contenido suficiente para generar cuestionario.",
    )
    quiz = generar_cuestionario(source_text, 10, args.course)
    if not quiz:
        raise RuntimeError("No se pudo generar el cuestionario.")

    quiz_path = write_markdown(
        lesson_dir / "cuestionario.md",
        note_frontmatter(args, "cuestionario"),
        quiz,
    )
    refresh_lesson_note(Path(args.note), lesson_dir)

    return {
        "ok": True,
        "message": "Cuestionario generado para la leccion activa.",
        "statuses": build_statuses(lesson_dir),
        "open_file": str(quiz_path),
    }


def action_refresh_note(args: argparse.Namespace) -> dict[str, object]:
    note_path = Path(args.note)
    lesson_dir = Path(args.lesson_dir)
    refresh_lesson_note(note_path, lesson_dir)
    return {
        "ok": True,
        "message": "La nota de la leccion fue actualizada con embeds y links actuales.",
        "statuses": build_statuses(lesson_dir),
        "open_file": str(note_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Acciones IA para lecciones Coursera desde Obsidian.")
    parser.add_argument(
        "action",
        choices=["process-full", "generate-report", "generate-audio", "generate-quiz", "refresh-note"],
    )
    parser.add_argument("--vault", required=True)
    parser.add_argument("--note", required=True)
    parser.add_argument("--lesson-dir", required=True)
    parser.add_argument("--course", required=True)
    parser.add_argument("--module", required=True)
    parser.add_argument("--lesson", required=True)
    parser.add_argument("--program", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    actions = {
        "process-full": action_process_full,
        "generate-report": action_generate_report,
        "generate-audio": action_generate_audio,
        "generate-quiz": action_generate_quiz,
        "refresh-note": action_refresh_note,
    }

    try:
        result = actions[args.action](args)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as error:
        print(json.dumps({"ok": False, "message": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
