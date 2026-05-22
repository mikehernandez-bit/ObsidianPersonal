"""
ObsidianAcademia - Constantes del Sistema
Enums, extensiones soportadas y nombres estándar.
"""

from enum import Enum


class FileType(Enum):
    """Tipos de archivo de entrada soportados."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    PDF = "pdf"
    MARKDOWN = "markdown"
    UNKNOWN = "unknown"


class SessionType(Enum):
    """Tipo de sesión universitaria."""
    TEORIA = "Teoria"
    PRACTICA = "Practica"


class ProcessingStatus(Enum):
    """Estado de procesamiento de un recurso."""
    PENDING = "pendiente"
    IN_PROGRESS = "en_proceso"
    COMPLETED = "completado"
    FAILED = "fallido"
    SKIPPED = "omitido"


class OutputType(Enum):
    """Tipos de producto de salida."""
    TRANSCRIPT = "transcript"
    SESSION_REPORT = "informe"
    SUMMARY = "resumen"
    QUIZ = "cuestionario"
    KEY_POINTS = "puntos_clave"
    PENDING_QUESTIONS = "dudas"
    NEXT_ACTIONS = "proximas_acciones"
    AUDIO_SCRIPT = "audio_script"
    TTS_AUDIO = "audio_tts"


# Extensiones de archivo soportadas
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".wma"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".webm", ".mov", ".wmv", ".flv"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
PDF_EXTENSIONS = {".pdf"}
MARKDOWN_EXTENSIONS = {".md"}

# Mapeo extensión → tipo
EXTENSION_MAP = {}
for ext in AUDIO_EXTENSIONS:
    EXTENSION_MAP[ext] = FileType.AUDIO
for ext in VIDEO_EXTENSIONS:
    EXTENSION_MAP[ext] = FileType.VIDEO
for ext in IMAGE_EXTENSIONS:
    EXTENSION_MAP[ext] = FileType.IMAGE
for ext in PDF_EXTENSIONS:
    EXTENSION_MAP[ext] = FileType.PDF
for ext in MARKDOWN_EXTENSIONS:
    EXTENSION_MAP[ext] = FileType.MARKDOWN

# Nombres de carpetas del vault
VAULT_DIRS = {
    "dashboard": "00_Dashboard",
    "university": "01_Universidad",
    "coursera": "02_Coursera",
    "materials": "03_Materiales",
    "processed": "04_Procesados",
    "templates": "05_Plantillas",
    "system": "06_Sistema",
}

# Subcarpetas de materiales
MATERIAL_SUBDIRS = ["Audios", "Videos", "Imagenes", "PDFs", "Otros"]

# Subcarpetas de procesados
PROCESSED_SUBDIRS = ["Transcripts", "AudiosTTS", "Metadata"]

# Nombres estándar de archivos de salida
OUTPUT_FILENAMES = {
    OutputType.TRANSCRIPT: "transcript.md",
    OutputType.SESSION_REPORT: "informe.md",
    OutputType.SUMMARY: "resumen.md",
    OutputType.QUIZ: "cuestionario.md",
    OutputType.KEY_POINTS: "puntos_clave.md",
    OutputType.PENDING_QUESTIONS: "dudas.md",
    OutputType.NEXT_ACTIONS: "proximas_acciones.md",
    OutputType.AUDIO_SCRIPT: "audio_script.md",
    OutputType.TTS_AUDIO: "audio_explicativo.wav",
}

# Frontmatter properties estándar
FRONTMATTER_KEYS = [
    "id",
    "tipo",
    "curso",
    "curso_nombre",
    "semana",
    "sesion",
    "fuente",
    "modalidad",
    "fecha",
    "estado",
    "transcript_status",
    "summary_status",
    "quiz_status",
    "audio_status",
    "input_files",
    "output_files",
    "tags",
]
