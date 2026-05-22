"""
ObsidianAcademia - Template Renderer
Renderiza plantillas Markdown con Jinja2, inyectando frontmatter YAML.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from src.utils.logger import get_logger

log = get_logger("template_renderer")

# Directorio de plantillas (relativo al proyecto)
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


def render_template(
    template_name: str,
    variables: dict,
    templates_dir: Optional[Path] = None,
) -> str:
    """
    Renderiza una plantilla Markdown con variables.
    
    Args:
        template_name: Nombre del archivo de plantilla (ej: "sesion.md").
        variables: Diccionario de variables a inyectar.
        templates_dir: Directorio de plantillas. Si es None, usa el default.
    
    Returns:
        Contenido Markdown renderizado.
    """
    if templates_dir is None:
        templates_dir = TEMPLATES_DIR

    template_path = templates_dir / template_name

    if not template_path.exists():
        log.error(f"Plantilla no encontrada: {template_path}")
        # Retornar contenido mínimo en vez de fallar
        return _minimal_template(template_name, variables)

    try:
        from jinja2 import Environment, FileSystemLoader

        env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            keep_trailing_newline=True,
        )

        template = env.get_template(template_name)

        # Añadir variables de contexto automáticas
        variables.setdefault("fecha", datetime.now().strftime("%Y-%m-%d"))
        variables.setdefault("fecha_hora", datetime.now().strftime("%Y-%m-%d %H:%M"))

        rendered = template.render(**variables)
        log.debug(f"Plantilla renderizada: {template_name}")
        return rendered

    except ImportError:
        log.warning("Jinja2 no instalado, usando renderizado simple")
        return _simple_render(template_path, variables)
    except Exception as e:
        log.error(f"Error al renderizar plantilla {template_name}: {e}")
        return _minimal_template(template_name, variables)


def build_frontmatter(metadata: dict) -> str:
    """
    Construye un bloque frontmatter YAML a partir de un diccionario.
    
    Args:
        metadata: Diccionario de propiedades.
    
    Returns:
        Bloque YAML entre separadores ---.
    """
    lines = ["---"]

    for key, value in metadata.items():
        if value is None:
            continue
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - \"{item}\"" if isinstance(item, str) else f"  - {item}")
        elif isinstance(value, bool):
            lines.append(f"{key}: {str(value).lower()}")
        elif isinstance(value, str) and any(c in value for c in ":#{}[]|>&*!"):
            lines.append(f'{key}: "{value}"')
        else:
            lines.append(f"{key}: {value}")

    lines.append("---")
    return "\n".join(lines)


def create_session_note(
    curso: str,
    curso_nombre: str,
    semana: int,
    tipo: str,
    fecha: str = "",
    contenido: str = "",
) -> str:
    """
    Crea una nota de sesión completa con frontmatter.
    
    Args:
        curso: ID del curso.
        curso_nombre: Nombre del curso.
        semana: Número de semana.
        tipo: "Teoria" o "Practica".
        fecha: Fecha de la sesión.
        contenido: Contenido adicional.
    
    Returns:
        Nota Markdown con frontmatter.
    """
    if not fecha:
        fecha = datetime.now().strftime("%Y-%m-%d")

    variables = {
        "id": f"{curso}_S{semana:02d}_{tipo}",
        "curso": curso,
        "curso_nombre": curso_nombre,
        "semana": semana,
        "tipo": tipo,
        "fecha": fecha,
        "contenido": contenido,
    }

    return render_template("sesion.md", variables)


def create_output_note(
    output_type: str,
    content: str,
    metadata: dict,
) -> str:
    """
    Crea una nota de producto derivado (resumen, quiz, etc.) con frontmatter.
    
    Args:
        output_type: Tipo de salida ("resumen", "cuestionario", etc.).
        content: Contenido generado por IA.
        metadata: Metadatos de la sesión origen.
    
    Returns:
        Nota Markdown con frontmatter y contenido.
    """
    # Template mapping
    template_map = {
        "resumen": "resumen.md",
        "cuestionario": "cuestionario.md",
        "informe": "informe_sesion.md",
        "puntos_clave": "resumen.md",
        "guion_audio": "audio_script.md",
        "dudas": "resumen.md",
        "proximas_acciones": "resumen.md",
    }

    template_name = template_map.get(output_type, "resumen.md")

    variables = {
        **metadata,
        "tipo_output": output_type,
        "contenido": content,
        "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    return render_template(template_name, variables)


def _simple_render(template_path: Path, variables: dict) -> str:
    """Renderizado simple con str.format si Jinja2 no está disponible."""
    try:
        content = template_path.read_text(encoding="utf-8")
        # Intentar reemplazar {{ variable }} por valor
        for key, value in variables.items():
            content = content.replace("{{ " + key + " }}", str(value))
            content = content.replace("{{" + key + "}}", str(value))
        return content
    except Exception:
        return _minimal_template(template_path.name, variables)


def _minimal_template(template_name: str, variables: dict) -> str:
    """Genera una nota mínima cuando la plantilla no está disponible."""
    fecha = variables.get("fecha", datetime.now().strftime("%Y-%m-%d"))
    titulo = variables.get("titulo", template_name.replace(".md", "").replace("_", " ").title())

    return f"""---
tipo: {variables.get('tipo', 'nota')}
fecha: {fecha}
---

# {titulo}

{variables.get('contenido', '*Contenido pendiente...*')}
"""
