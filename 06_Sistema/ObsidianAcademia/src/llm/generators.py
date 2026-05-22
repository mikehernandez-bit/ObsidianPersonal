"""
ObsidianAcademia - Generadores LLM
Funciones de alto nivel para generar productos académicos usando el LLM local.
"""

from pathlib import Path
from typing import Optional

from src.llm.client import get_llm_client
from src.llm.prompts import (
    SYSTEM_PROMPT,
    prompt_cuestionario,
    prompt_descripcion_imagen,
    prompt_dudas_pendientes,
    prompt_guion_audio,
    prompt_informe,
    prompt_proximas_acciones,
    prompt_puntos_clave,
    prompt_resumen,
)
from src.utils.logger import get_logger

log = get_logger("generators")


def _generate(prompt: str, product_name: str) -> Optional[str]:
    """Helper interno para generar contenido con logging consistente."""
    log.info(f"Generando: {product_name}...")
    client = get_llm_client()
    result = client.generate(prompt=prompt, system=SYSTEM_PROMPT)

    if result:
        log.info(f"✓ {product_name} generado ({len(result)} caracteres)")
    else:
        log.error(f"✗ Error al generar {product_name}")

    return result


def _generate_with_images(
    prompt: str,
    image_paths: list[Path],
    product_name: str,
) -> Optional[str]:
    """Helper interno para generar contenido multimodal con logging consistente."""
    log.info(f"Generando con vision: {product_name}...")
    client = get_llm_client()
    result = client.generate_with_images(
        prompt=prompt,
        image_paths=image_paths,
        system=SYSTEM_PROMPT,
    )

    if result:
        log.info(f"{product_name} multimodal generado ({len(result)} caracteres)")
    else:
        log.error(f"Error al generar {product_name} multimodal")

    return result


def generar_resumen(
    contenido: str,
    curso: str = "",
    semana: str = "",
    tipo: str = "",
) -> Optional[str]:
    """
    Genera un resumen estructurado del contenido.
    
    Args:
        contenido: Texto del contenido a resumir.
        curso: Nombre del curso.
        semana: Número/nombre de semana.
        tipo: "Teoria" o "Practica".
    
    Returns:
        Resumen en Markdown, o None si falla.
    """
    prompt = prompt_resumen(contenido, curso, semana, tipo)
    return _generate(prompt, "Resumen")


def generar_cuestionario(
    contenido: str,
    num_preguntas: int = 8,
    curso: str = "",
) -> Optional[str]:
    """
    Genera un cuestionario de estudio.
    
    Args:
        contenido: Texto del contenido.
        num_preguntas: Número de preguntas a generar.
        curso: Nombre del curso.
    
    Returns:
        Cuestionario en Markdown, o None si falla.
    """
    prompt = prompt_cuestionario(contenido, num_preguntas, curso)
    return _generate(prompt, "Cuestionario")


def generar_informe(
    contenido: str,
    curso: str = "",
    semana: str = "",
    tipo: str = "",
    fecha: str = "",
) -> Optional[str]:
    """
    Genera un informe de sesión.
    
    Args:
        contenido: Texto del contenido.
        curso: Nombre del curso.
        semana: Número/nombre de semana.
        tipo: Tipo de sesión.
        fecha: Fecha de la sesión.
    
    Returns:
        Informe en Markdown, o None si falla.
    """
    prompt = prompt_informe(contenido, curso, semana, tipo, fecha)
    return _generate(prompt, "Informe de sesión")


def generar_puntos_clave(
    contenido: str,
    curso: str = "",
) -> Optional[str]:
    """
    Genera lista de puntos clave.
    
    Args:
        contenido: Texto del contenido.
        curso: Nombre del curso.
    
    Returns:
        Puntos clave en Markdown, o None si falla.
    """
    prompt = prompt_puntos_clave(contenido, curso)
    return _generate(prompt, "Puntos clave")


def generar_guion_audio(
    contenido: str,
    curso: str = "",
    tema: str = "",
) -> Optional[str]:
    """
    Genera un guion para audio explicativo (TTS).
    
    Args:
        contenido: Texto del contenido.
        curso: Nombre del curso.
        tema: Tema específico.
    
    Returns:
        Guion en texto plano, o None si falla.
    """
    prompt = prompt_guion_audio(contenido, curso, tema)
    return _generate(prompt, "Guion de audio")


def generar_descripcion_imagen(
    image_path: Path,
    curso: str = "",
    tema: str = "",
) -> Optional[str]:
    """
    Genera una descripcion academica de una imagen usando vision real.
    """
    prompt = prompt_descripcion_imagen(
        curso=curso,
        tema=tema,
        archivo=image_path.name,
    )
    return _generate_with_images(
        prompt,
        [image_path],
        f"Descripcion de imagen {image_path.name}",
    )


def generar_dudas_pendientes(contenido: str) -> Optional[str]:
    """
    Identifica dudas y preguntas pendientes.
    
    Args:
        contenido: Texto del contenido.
    
    Returns:
        Lista de dudas en Markdown, o None si falla.
    """
    prompt = prompt_dudas_pendientes(contenido)
    return _generate(prompt, "Dudas pendientes")


def generar_proximas_acciones(
    contenido: str,
    curso: str = "",
) -> Optional[str]:
    """
    Genera lista de próximas acciones de estudio.
    
    Args:
        contenido: Texto del contenido.
        curso: Nombre del curso.
    
    Returns:
        Lista de acciones en Markdown, o None si falla.
    """
    prompt = prompt_proximas_acciones(contenido, curso)
    return _generate(prompt, "Próximas acciones")


def generar_todos(
    contenido: str,
    curso: str = "",
    semana: str = "",
    tipo: str = "",
    fecha: str = "",
    num_preguntas: int = 8,
) -> dict:
    """
    Genera TODOS los productos derivados de una sesión.
    Útil para el pipeline completo.
    
    Args:
        contenido: Texto consolidado del contenido.
        curso: Nombre del curso.
        semana: Número de semana.
        tipo: Tipo de sesión.
        fecha: Fecha de la sesión.
        num_preguntas: Número de preguntas para el quiz.
    
    Returns:
        Diccionario con todos los productos generados:
        {
            "resumen": str|None,
            "cuestionario": str|None,
            "informe": str|None,
            "puntos_clave": str|None,
            "guion_audio": str|None,
            "dudas": str|None,
            "proximas_acciones": str|None,
        }
    """
    log.info("=" * 50)
    log.info(f"Generando todos los productos para: {curso} - Semana {semana}")
    log.info("=" * 50)

    results = {}

    results["resumen"] = generar_resumen(contenido, curso, semana, tipo)
    results["cuestionario"] = generar_cuestionario(contenido, num_preguntas, curso)
    results["informe"] = generar_informe(contenido, curso, semana, tipo, fecha)
    results["puntos_clave"] = generar_puntos_clave(contenido, curso)
    results["guion_audio"] = generar_guion_audio(contenido, curso)
    results["dudas"] = generar_dudas_pendientes(contenido)
    results["proximas_acciones"] = generar_proximas_acciones(contenido, curso)

    # Resumen de resultados
    total = len(results)
    ok = sum(1 for v in results.values() if v is not None)
    log.info(f"Productos generados: {ok}/{total}")

    return results
