"""
ObsidianAcademia - Extractor OCR
Extrae texto de imágenes usando pytesseract (si disponible).
Fallback graceful si Tesseract no está instalado.
"""

from pathlib import Path
from typing import Optional

from src.utils.logger import get_logger

log = get_logger("ocr")

_tesseract_available: Optional[bool] = None


def _check_tesseract() -> bool:
    """Verifica si pytesseract y Tesseract OCR están disponibles."""
    global _tesseract_available

    if _tesseract_available is not None:
        return _tesseract_available

    try:
        import pytesseract
        # Intentar una operación simple para verificar que Tesseract está instalado
        pytesseract.get_tesseract_version()
        _tesseract_available = True
        log.info("Tesseract OCR disponible")
    except ImportError:
        _tesseract_available = False
        log.warning("pytesseract no instalado — OCR no disponible")
    except Exception:
        _tesseract_available = False
        log.warning(
            "Tesseract OCR no instalado en el sistema — OCR no disponible. "
            "Instálalo desde: https://github.com/UB-Mannheim/tesseract/wiki"
        )

    return _tesseract_available


def extract_text_from_image(
    image_path: Path,
    language: str = "spa",
) -> Optional[str]:
    """
    Extrae texto de una imagen usando OCR.
    
    Args:
        image_path: Ruta de la imagen.
        language: Código de idioma para Tesseract (defecto: "spa" para español).
    
    Returns:
        Texto extraído, o None si OCR no está disponible o falla.
    """
    if not image_path.exists():
        log.error(f"Imagen no encontrada: {image_path}")
        return None

    if not _check_tesseract():
        log.info(f"OCR no disponible. Imagen registrada: {image_path.name}")
        return None

    try:
        import pytesseract
        from PIL import Image

        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang=language)

        if text.strip():
            log.info(
                f"OCR extrajo {len(text)} caracteres de: {image_path.name}"
            )
            return text.strip()
        else:
            log.warning(f"OCR no encontró texto en: {image_path.name}")
            return ""

    except Exception as e:
        log.error(f"Error en OCR para {image_path.name}: {e}")
        return None


def create_image_note(
    image_path: Path,
    vault_root: Path,
    extracted_text: Optional[str] = None,
) -> str:
    """
    Crea contenido Markdown para una nota de imagen.
    Si hay texto OCR, lo incluye. Si no, deja placeholder.
    
    Args:
        image_path: Ruta de la imagen.
        vault_root: Raíz del vault para crear links relativos.
        extracted_text: Texto OCR extraído (si disponible).
    
    Returns:
        Contenido Markdown para la nota.
    """
    from src.utils.paths import format_path_for_obsidian

    rel_path = format_path_for_obsidian(image_path, vault_root)

    lines = [
        f"# Imagen: {image_path.stem}\n",
        f"![[{image_path.name}]]\n",
    ]

    if extracted_text:
        lines.append("## Texto extraído (OCR)\n")
        lines.append(extracted_text)
        lines.append("")
    else:
        lines.append("## Descripción\n")
        lines.append(
            "> [!NOTE] Descripción pendiente\n"
            "> OCR no disponible o no detectó texto.\n"
            "> Describe manualmente el contenido de esta imagen.\n"
        )
        lines.append("*Escribe aquí la descripción del contenido...*\n")

    return "\n".join(lines)
