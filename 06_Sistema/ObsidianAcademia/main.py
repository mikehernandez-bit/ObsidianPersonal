"""
ObsidianAcademia - CLI Principal
Interfaz de línea de comandos para todo el sistema.

Uso:
    python main.py [COMANDO] [OPCIONES]

Comandos principales:
    validate        Valida configuración y dependencias
    init-vault      Crea estructura inicial del vault
    init-course     Crea estructura de un curso
    process-audio   Procesa un archivo de audio
    process-video   Procesa un archivo de video
    process-image   Procesa una imagen
    process-session Pipeline completo de sesión
    process-coursera Procesa material de Coursera
    watch           Inicia watcher de carpetas
    status          Muestra estado del sistema
"""

import sys
from pathlib import Path

import click

# Añadir el directorio del proyecto al path
PROJECT_DIR = Path(__file__).parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


@click.group()
@click.option("--config", "-c", default=None, help="Ruta al archivo config.yaml")
@click.pass_context
def cli(ctx, config):
    """ObsidianAcademia — Sistema académico local-first para Obsidian."""
    ctx.ensure_object(dict)

    # Cargar configuración
    from src.config.settings import load_settings

    config_path = Path(config) if config else None
    settings = load_settings(config_path)
    ctx.obj["settings"] = settings


# ============================================================
# VALIDATE
# ============================================================
@cli.command()
@click.pass_context
def validate(ctx):
    """Valida la configuración y todas las dependencias del sistema."""
    from rich.console import Console
    from rich.table import Table

    from src.utils.validators import (
        validate_all_dependencies,
        validate_dir_exists,
        validate_ffmpeg,
        validate_ollama,
        validate_piper,
    )

    console = Console()
    settings = ctx.obj["settings"]
    all_ok = True

    console.print("\n[bold cyan]═══ ObsidianAcademia — Validación ═══[/bold cyan]\n")

    # Tabla de rutas
    table = Table(title="Rutas del sistema")
    table.add_column("Componente", style="cyan")
    table.add_column("Ruta", style="white")
    table.add_column("Estado", style="bold")

    paths_to_check = [
        ("Vault", settings.vault_path),
        ("FFmpeg", settings.ffmpeg_exe),
        ("FFprobe", settings.ffprobe_exe),
        ("Piper", settings.piper_exe),
        ("Modelo Piper", settings.piper_model),
    ]

    for name, path in paths_to_check:
        exists = path.exists()
        status = "[green]✓[/green]" if exists else "[red]✗[/red]"
        table.add_row(name, str(path), status)
        if not exists:
            all_ok = False

    console.print(table)

    # Validar FFmpeg
    console.print("\n[bold yellow]FFmpeg:[/bold yellow]")
    if not validate_ffmpeg(settings.ffmpeg_exe, settings.ffprobe_exe):
        all_ok = False
        console.print("  [red]FFmpeg no funcional. Ejecuta install.ps1[/red]")

    # Validar Piper
    console.print("\n[bold yellow]Piper TTS:[/bold yellow]")
    if not validate_piper(settings.piper_exe, settings.piper_model, settings.piper_config):
        all_ok = False
        console.print("  [red]Piper no funcional[/red]")

    # Validar Ollama
    console.print("\n[bold yellow]Ollama (LLM):[/bold yellow]")
    if not validate_ollama(settings.llm_endpoint, settings.llm_model):
        all_ok = False
        console.print("  [red]Ollama no disponible. Ejecuta: ollama serve[/red]")

    # Validar paquetes Python
    console.print("\n[bold yellow]Paquetes Python:[/bold yellow]")
    pkg_status = validate_all_dependencies()
    for pkg, ok in pkg_status.items():
        if not ok and "opcional" not in pkg.lower():
            all_ok = False

    # Resultado final
    console.print("\n" + "═" * 50)
    if all_ok:
        console.print("[bold green]✓ Todo listo. El sistema está operativo.[/bold green]")
    else:
        console.print(
            "[bold red]✗ Hay problemas que resolver. "
            "Revisa los errores arriba.[/bold red]"
        )
    console.print("")


# ============================================================
# INIT-VAULT
# ============================================================
@cli.command("init-vault")
@click.pass_context
def init_vault(ctx):
    """Crea la estructura inicial de carpetas en el vault de Obsidian."""
    from src.config.constants import MATERIAL_SUBDIRS, PROCESSED_SUBDIRS, VAULT_DIRS
    from src.obsidian.vault_writer import VaultWriter
    from src.obsidian.template_renderer import render_template
    from rich.console import Console

    console = Console()
    settings = ctx.obj["settings"]
    writer = VaultWriter()
    vault = settings.vault_path

    console.print("\n[bold cyan]Inicializando vault...[/bold cyan]\n")

    # Crear carpetas principales
    for key, dirname in VAULT_DIRS.items():
        dir_path = vault / dirname
        dir_path.mkdir(parents=True, exist_ok=True)
        console.print(f"  📁 {dirname}")

    # Crear subcarpetas de materiales
    for subdir in MATERIAL_SUBDIRS:
        dir_path = vault / VAULT_DIRS["materials"] / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
        console.print(f"    📂 {VAULT_DIRS['materials']}/{subdir}")

    # Crear subcarpetas de procesados
    for subdir in PROCESSED_SUBDIRS:
        dir_path = vault / VAULT_DIRS["processed"] / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
        console.print(f"    📂 {VAULT_DIRS['processed']}/{subdir}")

    # Crear Dashboard
    dashboard_content = """---
tipo: dashboard
fecha: """ + __import__("datetime").datetime.now().strftime("%Y-%m-%d") + """
tags:
  - dashboard
  - sistema
---

# 🎓 Dashboard Académico

## Cursos activos

```dataview
TABLE curso_nombre as "Curso", estado as "Estado"
FROM "01_Universidad"
WHERE tipo = "curso"
SORT curso_nombre ASC
```

## Sesiones recientes

```dataview
TABLE curso_nombre as "Curso", semana as "Semana", sesion as "Tipo", fecha as "Fecha"
FROM "01_Universidad"
WHERE tipo = "sesion"
SORT fecha DESC
LIMIT 10
```

## Tareas pendientes

```dataview
TASK
FROM "01_Universidad"
WHERE !completed
SORT fecha ASC
```

## Coursera

```dataview
TABLE curso as "Curso", modulo as "Módulo", estado as "Estado"
FROM "02_Coursera"
WHERE tipo = "leccion_coursera"
SORT fecha DESC
LIMIT 10
```
"""
    writer.write_note(f"{VAULT_DIRS['dashboard']}/Dashboard.md", dashboard_content, overwrite=True)
    console.print("  📝 Dashboard.md creado")

    # Crear índice de Universidad
    uni_index = """---
tipo: indice
fecha: """ + __import__("datetime").datetime.now().strftime("%Y-%m-%d") + """
tags:
  - indice
  - universidad
---

# 📚 Cursos Universitarios

```dataview
TABLE curso_nombre as "Nombre", code as "Código", estado as "Estado"
FROM "01_Universidad"
WHERE tipo = "curso"
SORT curso_nombre ASC
```
"""
    writer.write_note(f"{VAULT_DIRS['university']}/_index.md", uni_index, overwrite=True)

    # Crear índice de Coursera
    coursera_index = """---
tipo: indice
fecha: """ + __import__("datetime").datetime.now().strftime("%Y-%m-%d") + """
tags:
  - indice
  - coursera
---

# 🌐 Coursera

```dataview
TABLE curso as "Curso", modulo as "Módulo", leccion as "Lección", estado as "Estado"
FROM "02_Coursera"
WHERE tipo = "leccion_coursera"
SORT fecha DESC
```
"""
    writer.write_note(f"{VAULT_DIRS['coursera']}/_index.md", coursera_index, overwrite=True)

    # Copiar plantillas al vault
    templates_src = PROJECT_DIR / "templates"
    templates_dst = vault / VAULT_DIRS["templates"]
    templates_dst.mkdir(parents=True, exist_ok=True)

    if templates_src.exists():
        import shutil
        for template_file in templates_src.glob("*.md"):
            shutil.copy2(template_file, templates_dst / template_file.name)
            console.print(f"  📄 Plantilla: {template_file.name}")

    console.print(f"\n[bold green]✓ Vault inicializado en: {vault}[/bold green]\n")


# ============================================================
# INIT-COURSE
# ============================================================
@cli.command("init-course")
@click.option("--id", "course_id", help="ID del curso (de config.yaml)")
@click.option("--name", "course_name", help="Nombre del curso")
@click.option("--all", "all_courses", is_flag=True, help="Crear todos los cursos de config.yaml")
@click.pass_context
def init_course(ctx, course_id, course_name, all_courses):
    """Crea la estructura de carpetas para un curso universitario."""
    from src.obsidian.vault_writer import VaultWriter
    from src.obsidian.template_renderer import build_frontmatter
    from rich.console import Console

    console = Console()
    settings = ctx.obj["settings"]
    writer = VaultWriter()

    courses = []

    if all_courses:
        courses = [(c.id, c.name) for c in settings.courses]
    elif course_id:
        course = settings.get_course(course_id)
        if course:
            courses = [(course.id, course.name)]
        else:
            console.print(f"[red]Curso '{course_id}' no encontrado en config.yaml[/red]")
            return
    elif course_name:
        cid = course_id or course_name.lower().replace(" ", "_")[:20]
        courses = [(cid, course_name)]
    else:
        console.print("[red]Especifica --id, --name, o --all[/red]")
        return

    fecha = __import__("datetime").datetime.now().strftime("%Y-%m-%d")

    for cid, cname in courses:
        console.print(f"\n[bold cyan]Creando curso: {cname} ({cid})[/bold cyan]")

        course_dir = f"01_Universidad/Curso_{cid}"

        # Crear nota del curso
        frontmatter = build_frontmatter({
            "tipo": "curso",
            "id": cid,
            "curso_nombre": cname,
            "ciclo": settings.current_cycle,
            "semanas_total": settings.total_weeks,
            "estado": "activo",
            "fecha_inicio": fecha,
            "tags": ["academia", "curso", cid],
        })

        curso_content = f"""{frontmatter}

# {cname}

**Ciclo:** {settings.current_cycle}
**Semanas:** {settings.total_weeks}

## Sesiones

```dataview
TABLE semana as "Semana", sesion as "Tipo", estado as "Estado", fecha as "Fecha"
FROM "01_Universidad"
WHERE tipo = "sesion" AND curso_nombre = this.curso_nombre
SORT semana ASC
```

## Resúmenes

```dataview
LIST
FROM "01_Universidad"
WHERE tipo = "resumen" AND curso_nombre = this.curso_nombre
SORT semana ASC
```
"""
        writer.write_note(f"{course_dir}/_curso.md", curso_content, overwrite=True)
        console.print(f"  📝 _curso.md")

        # Crear estructura de semanas
        for week in range(1, settings.total_weeks + 1):
            week_dir = f"{course_dir}/Semana_{week:02d}"
            (settings.vault_path / week_dir / "Teoria").mkdir(parents=True, exist_ok=True)
            (settings.vault_path / week_dir / "Practica").mkdir(parents=True, exist_ok=True)
            (settings.vault_path / week_dir / "Material").mkdir(parents=True, exist_ok=True)

            # Nota de semana
            week_frontmatter = build_frontmatter({
                "tipo": "semana",
                "curso": cid,
                "curso_nombre": cname,
                "semana": week,
                "estado": "pendiente",
                "tags": ["academia", "semana", cid],
            })

            week_content = f"""{week_frontmatter}

# Semana {week} — {cname}

## Teoría
```dataview
LIST
FROM "01_Universidad"
WHERE (tipo = "sesion_teoria" OR (tipo = "sesion" AND sesion = "Teoria")) AND curso = "{cid}" AND semana = {week}
SORT file.name ASC
```

## Práctica
```dataview
LIST
FROM "01_Universidad"
WHERE (tipo = "sesion_practica" OR (tipo = "sesion" AND sesion = "Practica")) AND curso = "{cid}" AND semana = {week}
SORT file.name ASC
```
"""
            writer.write_note(f"{week_dir}/_semana.md", week_content, overwrite=True)

        console.print(f"  📁 {settings.total_weeks} semanas creadas (Teoria + Practica + Material)")

        # Crear carpeta de tareas
        tareas_dir = f"{course_dir}/Tareas"
        (settings.vault_path / tareas_dir).mkdir(parents=True, exist_ok=True)
        console.print(f"  📁 Tareas")

    console.print(f"\n[bold green]✓ {len(courses)} curso(s) inicializado(s)[/bold green]\n")


# ============================================================
# PROCESS-AUDIO
# ============================================================
@cli.command("process-audio")
@click.argument("path", type=click.Path(exists=True))
@click.option("--curso", "-cu", default="", help="ID del curso")
@click.option("--semana", "-s", default=0, type=int, help="Número de semana")
@click.option("--tipo", "-t", default="Teoria", type=click.Choice(["Teoria", "Practica"]))
@click.option("--no-tts", is_flag=True, help="No generar audio TTS")
@click.pass_context
def process_audio_cmd(ctx, path, curso, semana, tipo, no_tts):
    """Procesa un archivo de audio: transcripción + IA + TTS."""
    from src.pipelines.audio_pipeline import process_audio

    settings = ctx.obj["settings"]
    course = settings.get_course(curso) if curso else None

    results = process_audio(
        audio_path=Path(path),
        curso=curso,
        curso_nombre=course.name if course else "",
        semana=semana,
        tipo=tipo,
        generate_tts=not no_tts,
    )

    _print_results(results)


# ============================================================
# PROCESS-VIDEO
# ============================================================
@cli.command("process-video")
@click.argument("path", type=click.Path(exists=True))
@click.option("--curso", "-cu", default="", help="ID del curso")
@click.option("--semana", "-s", default=0, type=int, help="Número de semana")
@click.option("--tipo", "-t", default="Teoria", type=click.Choice(["Teoria", "Practica"]))
@click.option("--no-tts", is_flag=True, help="No generar audio TTS")
@click.pass_context
def process_video_cmd(ctx, path, curso, semana, tipo, no_tts):
    """Procesa un archivo de video: extracción → transcripción → IA → TTS."""
    from src.pipelines.video_pipeline import process_video

    settings = ctx.obj["settings"]
    course = settings.get_course(curso) if curso else None

    results = process_video(
        video_path=Path(path),
        curso=curso,
        curso_nombre=course.name if course else "",
        semana=semana,
        tipo=tipo,
        generate_tts=not no_tts,
    )

    _print_results(results)


# ============================================================
# PROCESS-IMAGE
# ============================================================
@cli.command("process-image")
@click.argument("path", type=click.Path(exists=True))
@click.option("--curso", "-cu", default="", help="ID del curso")
@click.option("--semana", "-s", default=0, type=int, help="Número de semana")
@click.option("--tipo", "-t", default="Teoria", type=click.Choice(["Teoria", "Practica"]))
@click.pass_context
def process_image_cmd(ctx, path, curso, semana, tipo):
    """Procesa una imagen: OCR → IA."""
    from src.pipelines.image_pipeline import process_image

    settings = ctx.obj["settings"]
    course = settings.get_course(curso) if curso else None

    results = process_image(
        image_path=Path(path),
        curso=curso,
        curso_nombre=course.name if course else "",
        semana=semana,
        tipo=tipo,
    )

    _print_results(results)


# ============================================================
# PROCESS-SESSION
# ============================================================
@cli.command("process-session")
@click.option("--curso", "-cu", required=True, help="ID del curso")
@click.option("--semana", "-s", required=True, type=int, help="Número de semana")
@click.option("--tipo", "-t", required=True, type=click.Choice(["Teoria", "Practica"]))
@click.option("--files", "-f", multiple=True, type=click.Path(exists=True), help="Archivos de entrada")
@click.option("--dir", "-d", "input_dir", type=click.Path(exists=True), help="Directorio con archivos de entrada")
@click.option("--no-tts", is_flag=True, help="No generar audio TTS")
@click.option("--nota", "-n", default=None, help="Texto de notas adicional")
@click.pass_context
def process_session_cmd(ctx, curso, semana, tipo, files, input_dir, no_tts, nota):
    """Pipeline completo de sesión: procesa todos los archivos."""
    from src.pipelines.session_pipeline import process_session
    from src.ingestion.detector import find_files_in_dir

    settings = ctx.obj["settings"]
    course = settings.get_course(curso)

    if not course:
        click.echo(f"Error: Curso '{curso}' no encontrado en config.yaml")
        return

    # Recopilar archivos de entrada
    input_files = [Path(f) for f in files]

    if input_dir:
        dir_files = find_files_in_dir(Path(input_dir))
        input_files.extend(dir_files)

    if not input_files:
        click.echo("Error: No se especificaron archivos de entrada. Usa --files o --dir")
        return

    results = process_session(
        input_files=input_files,
        curso=curso,
        curso_nombre=course.name,
        semana=semana,
        tipo=tipo,
        generate_tts=not no_tts,
        note_content=nota,
    )

    _print_results(results)


# ============================================================
# PROCESS-COURSERA
# ============================================================
@cli.command("process-coursera")
@click.option("--course", "-c", required=True, help="Nombre del curso de Coursera")
@click.option("--module", "-m", required=True, help="Nombre del módulo")
@click.option("--lesson", "-l", required=True, help="Nombre de la lección")
@click.option("--program", "-p", default=None, help="Nombre del programa (opcional)")
@click.option("--files", "-f", multiple=True, type=click.Path(exists=True), help="Archivos de entrada")
@click.option("--dir", "-d", "input_dir", type=click.Path(exists=True), help="Directorio con archivos")
@click.option("--no-tts", is_flag=True, help="No generar audio TTS")
@click.option("--nota", "-n", default=None, help="Notas adicionales")
@click.pass_context
def process_coursera_cmd(ctx, course, module, lesson, program, files, input_dir, no_tts, nota):
    """Procesa una lección de Coursera."""
    from src.pipelines.coursera_pipeline import process_coursera_lesson
    from src.ingestion.detector import find_files_in_dir

    input_files = [Path(f) for f in files]

    if input_dir:
        dir_files = find_files_in_dir(Path(input_dir))
        input_files.extend(dir_files)

    if not input_files and not nota:
        click.echo("Error: Especifica archivos (--files/--dir) o notas (--nota)")
        return

    results = process_coursera_lesson(
        input_files=input_files,
        course_name=course,
        module_name=module,
        lesson_name=lesson,
        program_name=program,
        generate_tts=not no_tts,
        note_content=nota,
    )

    _print_results(results)


# ============================================================
# WATCH
# ============================================================
@cli.command()
@click.pass_context
def watch(ctx):
    """Inicia el watcher automático de carpetas."""
    from src.watcher.folder_watcher import start_watcher
    start_watcher()


# ============================================================
# STATUS
# ============================================================
@cli.command()
@click.pass_context
def status(ctx):
    """Muestra el estado actual del sistema."""
    from rich.console import Console
    from rich.table import Table

    console = Console()
    settings = ctx.obj["settings"]

    console.print("\n[bold cyan]═══ ObsidianAcademia — Estado ═══[/bold cyan]\n")

    # Información general
    console.print(f"[bold]Vault:[/bold] {settings.vault_path}")
    console.print(f"[bold]Modelo LLM:[/bold] {settings.llm_model}")
    console.print(f"[bold]Ciclo:[/bold] {settings.current_cycle}")
    console.print(f"[bold]Cursos:[/bold] {len(settings.courses)}")

    # Tabla de cursos
    if settings.courses:
        table = Table(title="\nCursos configurados")
        table.add_column("ID", style="cyan")
        table.add_column("Nombre", style="white")
        table.add_column("Código", style="yellow")

        for course in settings.courses:
            table.add_row(course.id, course.name, course.code)

        console.print(table)

    # Contar archivos procesados
    processed_dir = settings.vault_path / "04_Procesados"
    if processed_dir.exists():
        transcript_count = len(list(processed_dir.glob("**/*.md")))
        audio_count = len(list(processed_dir.glob("**/*.wav")))
        console.print(f"\n[bold]Archivos procesados:[/bold]")
        console.print(f"  📝 Transcripts/Notas: {transcript_count}")
        console.print(f"  🔊 Audios TTS: {audio_count}")

    console.print("")


# ============================================================
# INIT-WEEK
# ============================================================
@cli.command("init-week")
@click.option("--curso", "-cu", required=True, help="ID del curso")
@click.option("--semana", "-s", required=True, type=int, help="Número de semana")
@click.pass_context
def init_week(ctx, curso, semana):
    """Crea la estructura de una semana específica para un curso."""
    from src.obsidian.template_renderer import build_frontmatter
    from src.obsidian.vault_writer import VaultWriter
    from rich.console import Console

    console = Console()
    settings = ctx.obj["settings"]
    course = settings.get_course(curso)

    if not course:
        console.print(f"[red]Curso '{curso}' no encontrado[/red]")
        return

    writer = VaultWriter()
    week_dir = f"01_Universidad/Curso_{curso}/Semana_{semana:02d}"

    (settings.vault_path / week_dir / "Teoria").mkdir(parents=True, exist_ok=True)
    (settings.vault_path / week_dir / "Practica").mkdir(parents=True, exist_ok=True)
    (settings.vault_path / week_dir / "Material").mkdir(parents=True, exist_ok=True)

    frontmatter = build_frontmatter({
        "tipo": "semana",
        "curso": curso,
        "curso_nombre": course.name,
        "semana": semana,
        "estado": "pendiente",
        "tags": ["academia", "semana", curso],
    })

    content = f"""{frontmatter}

# Semana {semana} — {course.name}

## Teoría
```dataview
LIST
FROM "01_Universidad"
WHERE (tipo = "sesion_teoria" OR (tipo = "sesion" AND sesion = "Teoria")) AND curso = "{curso}" AND semana = {semana}
SORT file.name ASC
```

## Práctica
```dataview
LIST
FROM "01_Universidad"
WHERE (tipo = "sesion_practica" OR (tipo = "sesion" AND sesion = "Practica")) AND curso = "{curso}" AND semana = {semana}
SORT file.name ASC
```
"""

    writer.write_note(f"{week_dir}/_semana.md", content, overwrite=True)
    console.print(f"[green]✓ Semana {semana} creada para {course.name}[/green]")


# ============================================================
# Utilidades
# ============================================================
def _print_results(results: dict):
    """Imprime los resultados de un pipeline."""
    try:
        from rich.console import Console
        from rich.table import Table

        console = Console()

        status = results.get("status", "unknown")
        status_color = {
            "completed": "green",
            "partial": "yellow",
            "failed": "red",
        }.get(status, "white")

        console.print(f"\n[bold {status_color}]Estado: {status}[/bold {status_color}]")

        # Tabla de outputs
        outputs = results.get("outputs", {})
        if outputs:
            table = Table(title="Archivos generados")
            table.add_column("Producto", style="cyan")
            table.add_column("Ruta", style="white")

            for key, path in outputs.items():
                table.add_row(key, str(path))

            console.print(table)

        # Errores
        errors = results.get("errors", [])
        if errors:
            console.print("\n[bold red]Errores:[/bold red]")
            for err in errors:
                console.print(f"  ✗ {err}")

        console.print("")

    except ImportError:
        # Fallback sin Rich
        print(f"\nEstado: {results.get('status', 'unknown')}")
        for key, path in results.get("outputs", {}).items():
            print(f"  {key}: {path}")
        for err in results.get("errors", []):
            print(f"  ERROR: {err}")


if __name__ == "__main__":
    cli()
