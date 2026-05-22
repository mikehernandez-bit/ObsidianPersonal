"""
ObsidianAcademia - Extractor de PDF
Extrae texto de archivos PDF usando PyMuPDF (fitz).
"""

from pathlib import Path
from typing import Optional

from src.utils.logger import get_logger

log = get_logger("pdf_extractor")


def extract_text_from_pdf(pdf_path: Path) -> Optional[str]:
    """
    Extrae texto completo de un archivo PDF.
    
    Args:
        pdf_path: Ruta del archivo PDF.
    
    Returns:
        Texto extraído del PDF, o None si falla.
    """
    if not pdf_path.exists():
        log.error(f"PDF no encontrado: {pdf_path}")
        return None

    try:
        import fitz  # PyMuPDF
    except ImportError:
        log.error("PyMuPDF no instalado. Ejecuta: pip install PyMuPDF")
        return None

    try:
        doc = fitz.open(str(pdf_path))
        pages_text = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text.strip():
                pages_text.append(f"<!-- Página {page_num + 1} -->\n{text.strip()}")

        doc.close()

        if pages_text:
            full_text = "\n\n---\n\n".join(pages_text)
            log.info(
                f"PDF extraído: {pdf_path.name} — "
                f"{len(pages_text)} páginas, {len(full_text)} caracteres"
            )
            return full_text
        else:
            log.warning(
                f"PDF sin texto extraíble: {pdf_path.name} "
                "(puede ser un PDF escaneado)"
            )
            return ""

    except Exception as e:
        log.error(f"Error al extraer PDF {pdf_path.name}: {e}")
        return None


def extract_pdf_metadata(pdf_path: Path) -> Optional[dict]:
    """
    Extrae metadatos de un PDF (título, autor, etc.).
    
    Args:
        pdf_path: Ruta del archivo PDF.
    
    Returns:
        Diccionario con metadatos, o None si falla.
    """
    try:
        import fitz

        doc = fitz.open(str(pdf_path))
        metadata = doc.metadata
        page_count = len(doc)
        doc.close()

        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "pages": page_count,
            "filename": pdf_path.name,
        }

    except ImportError:
        log.warning("PyMuPDF no instalado, no se pueden extraer metadatos")
        return None
    except Exception as e:
        log.error(f"Error al extraer metadatos de {pdf_path.name}: {e}")
        return None
