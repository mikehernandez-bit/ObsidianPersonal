"""
ObsidianAcademia - Folder Watcher
Monitoreo automático de carpetas para procesamiento de archivos nuevos.
"""

import time
from pathlib import Path
from typing import Set

from src.config.constants import FileType
from src.config.settings import get_settings
from src.ingestion.detector import detect_file_type
from src.utils.logger import get_logger

log = get_logger("watcher")

# Archivos ya procesados (para evitar duplicados)
_processed_files: Set[str] = set()


def start_watcher():
    """
    Inicia el watcher de carpetas usando watchdog.
    Monitorea las carpetas configuradas y procesa archivos nuevos.
    """
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        log.error("watchdog no instalado. Ejecuta: pip install watchdog")
        return

    settings = get_settings()

    class AcademiaHandler(FileSystemEventHandler):
        """Handler para eventos de archivos nuevos."""

        def __init__(self):
            super().__init__()
            self._debounce = {}

        def on_created(self, event):
            if event.is_directory:
                return

            file_path = Path(event.src_path)

            # Verificar extensión
            ext = file_path.suffix.lower()
            if settings.watcher_extensions and ext not in settings.watcher_extensions:
                return

            # Debounce: esperar a que el archivo se termine de escribir
            file_key = str(file_path)
            current_time = time.time()

            if file_key in self._debounce:
                if current_time - self._debounce[file_key] < 2:
                    return

            self._debounce[file_key] = current_time

            # Evitar reprocesar
            if file_key in _processed_files:
                return

            log.info(f"Nuevo archivo detectado: {file_path.name}")
            _process_detected_file(file_path)
            _processed_files.add(file_key)

        def on_modified(self, event):
            # Ignorar modificaciones, solo archivos nuevos
            pass

    # Configurar carpetas a monitorear
    watch_paths = [
        settings.input_audios,
        settings.input_videos,
        settings.input_imagenes,
        settings.input_pdfs,
    ]

    # Asegurar que las carpetas existan
    for wp in watch_paths:
        wp.mkdir(parents=True, exist_ok=True)

    observer = Observer()
    handler = AcademiaHandler()

    for watch_path in watch_paths:
        if watch_path.exists():
            observer.schedule(handler, str(watch_path), recursive=False)
            log.info(f"Monitoreando: {watch_path}")

    observer.start()
    log.info("=" * 50)
    log.info("Watcher iniciado. Presiona Ctrl+C para detener.")
    log.info("=" * 50)

    try:
        while True:
            time.sleep(settings.watcher_poll_interval)
    except KeyboardInterrupt:
        log.info("Watcher detenido por el usuario")
        observer.stop()

    observer.join()


def _process_detected_file(file_path: Path):
    """Procesa un archivo detectado por el watcher."""
    file_type = detect_file_type(file_path)

    try:
        if file_type == FileType.AUDIO:
            from src.pipelines.audio_pipeline import process_audio
            log.info(f"Procesando audio: {file_path.name}")
            process_audio(file_path)

        elif file_type == FileType.VIDEO:
            from src.pipelines.video_pipeline import process_video
            log.info(f"Procesando video: {file_path.name}")
            process_video(file_path)

        elif file_type == FileType.IMAGE:
            from src.pipelines.image_pipeline import process_image
            log.info(f"Procesando imagen: {file_path.name}")
            process_image(file_path)

        elif file_type == FileType.PDF:
            log.info(f"PDF detectado: {file_path.name}")
            log.info("Usa 'process-session' para procesar PDFs con contexto completo")

        else:
            log.debug(f"Archivo no procesable: {file_path.name}")

    except Exception as e:
        log.error(f"Error procesando {file_path.name}: {e}")
