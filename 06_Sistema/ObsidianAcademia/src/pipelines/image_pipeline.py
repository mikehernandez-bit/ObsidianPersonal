"""
ObsidianAcademia - Image Pipeline
Pipeline: imagen → OCR → IA → productos → vault.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config.settings import get_settings
from src.extraction.ocr_extractor import create_image_note, extract_text_from_image
from src.llm.generators import generar_resumen, generar_puntos_clave
from src.obsidian.template_renderer import build_frontmatter
from src.obsidian.writer_factory import get_writer
from src.utils.logger import get_logger
from src.utils.paths import ensure_dir

log = get_logger("image_pipeline")


def process_image(
    image_path: Path,
    output_dir: Optional[Path] = None,
    curso: str = "",
    curso_nombre: str = "",
    semana: int = 0,
    tipo: str = "",
) -> dict:
    """
    Pipeline para procesar una imagen (pizarra, diapositiva, cuaderno).
    
    Flujo:
    1. Extraer texto con OCR (si disponible)
    2. Crear nota con imagen embebida
    3. Si hay texto, generar resumen y puntos clave
    
    Args:
        image_path: Ruta de la imagen.
        output_dir: Directorio de salida.
        curso: ID del curso.
        curso_nombre: Nombre del curso.
        semana: Número de semana.
        tipo: "Teoria" o "Practica".
    
    Returns:
        Diccionario con resultados.
    """
    results = {
        "status": "started",
        "source": str(image_path),
        "outputs": {},
        "errors": [],
    }

    settings = get_settings()

    if not image_path.exists():
        results["status"] = "failed"
        results["errors"].append("Imagen no encontrada")
        return results

    if output_dir is None:
        if curso and semana and tipo:
            from src.utils.paths import build_session_path
            output_dir = build_session_path(
                settings.vault_path, curso, semana, tipo
            )
        else:
            output_dir = settings.vault_path / "04_Procesados" / image_path.stem

    ensure_dir(output_dir)
    log.info(f"=== Image Pipeline: {image_path.name} ===")

    # --- Paso 1: OCR ---
    log.info("[1/3] Extrayendo texto con OCR...")
    extracted_text = extract_text_from_image(image_path)

    # --- Paso 2: Crear nota de imagen ---
    log.info("[2/3] Creando nota de imagen...")
    writer = get_writer()
    fecha = datetime.now().strftime("%Y-%m-%d")

    image_note = create_image_note(image_path, settings.vault_path, extracted_text)

    frontmatter = build_frontmatter({
        "tipo": "imagen",
        "curso": curso,
        "semana": semana,
        "sesion": tipo,
        "fecha": fecha,
        "fuente": image_path.name,
        "ocr_status": "completado" if extracted_text else "no_disponible",
        "tags": ["academia", "imagen", curso],
    })

    full_content = f"{frontmatter}\n\n{image_note}"
    note_path = output_dir / f"imagen_{image_path.stem}.md"
    written = writer.write_note_absolute(note_path, full_content, overwrite=True)
    if written:
        results["outputs"]["image_note"] = str(written)

    # --- Paso 3: Generar productos IA si hay texto ---
    if extracted_text and len(extracted_text) > 50:
        log.info("[3/3] Generando productos IA del texto extraído...")

        resumen = generar_resumen(
            extracted_text, curso_nombre or curso, str(semana), tipo
        )
        if resumen:
            resumen_path = output_dir / f"resumen_imagen_{image_path.stem}.md"
            res_frontmatter = build_frontmatter({
                "tipo": "resumen",
                "fuente": image_path.name,
                "fecha": fecha,
                "tags": ["academia", "resumen", "imagen"],
            })
            writer.write_note_absolute(
                resumen_path, f"{res_frontmatter}\n\n{resumen}", overwrite=True
            )
            results["outputs"]["resumen"] = str(resumen_path)

        puntos = generar_puntos_clave(extracted_text, curso_nombre or curso)
        if puntos:
            puntos_path = output_dir / f"puntos_clave_imagen_{image_path.stem}.md"
            pk_frontmatter = build_frontmatter({
                "tipo": "puntos_clave",
                "fuente": image_path.name,
                "fecha": fecha,
                "tags": ["academia", "puntos_clave", "imagen"],
            })
            writer.write_note_absolute(
                puntos_path, f"{pk_frontmatter}\n\n{puntos}", overwrite=True
            )
            results["outputs"]["puntos_clave"] = str(puntos_path)
    else:
        log.info("[3/3] Sin texto suficiente para IA — omitido")

    results["status"] = "completed" if not results["errors"] else "partial"
    log.info(f"=== Image Pipeline completado: {results['status']} ===")
    return results
