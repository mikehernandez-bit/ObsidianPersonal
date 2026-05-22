"""
ObsidianAcademia - Configuración del Sistema
Carga, valida y expone la configuración desde config.yaml.
Patrón Singleton para acceso global.
"""

import os
from pathlib import Path
from typing import Any, Optional

import yaml

from src.utils.logger import get_logger, setup_logger

log = get_logger("config")

# Singleton de configuración
_config_instance: Optional["Settings"] = None


class CourseConfig:
    """Configuración de un curso universitario."""

    def __init__(self, data: dict):
        self.id: str = data.get("id", "")
        self.name: str = data.get("name", "")

    def __repr__(self) -> str:
        return f"CourseConfig(id={self.id}, name={self.name})"


class Settings:
    """Configuración global del sistema, cargada desde config.yaml."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Carga la configuración desde un archivo YAML.
        
        Args:
            config_path: Ruta al archivo config.yaml.
                          Si es None, busca en la raíz del proyecto.
        """
        if config_path is None:
            # Buscar config.yaml relativo a la raíz del proyecto
            config_path = Path(__file__).parent.parent.parent / "config.yaml"

        self.config_path = config_path.resolve()

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Archivo de configuración no encontrado: {self.config_path}"
            )

        with open(self.config_path, "r", encoding="utf-8") as f:
            self._raw = yaml.safe_load(f) or {}

        self._load_config()

    def _resolve_path(self, raw_path: str, *, base_dir: Path | None = None) -> Path:
        """Resuelve rutas relativas usando la carpeta del config como base."""
        base = base_dir or self.config_path.parent
        path = Path(raw_path)
        if not path.is_absolute():
            path = base / path
        return path.resolve()

    def _load_config(self):
        """Carga y asigna todas las propiedades de configuración."""
        # -- Vault --
        vault = self._raw.get("vault", {})
        vault_path_raw = os.environ.get(
            "OBSIDIAN_ACADEMIA_VAULT_PATH",
            vault.get("path", ""),
        )
        self.vault_path = self._resolve_path(vault_path_raw, base_dir=self.config_path.parent)
        self.use_rest_api = vault.get("use_rest_api", False)
        self.rest_api_url = vault.get("rest_api_url", "http://127.0.0.1:27124")
        self.rest_api_key = vault.get("rest_api_key", "")

        # -- Input paths (relativos al vault) --
        inp = self._raw.get("input", {})
        self.input_audios = self.vault_path / inp.get("audios", "03_Materiales\\Audios")
        self.input_videos = self.vault_path / inp.get("videos", "03_Materiales\\Videos")
        self.input_imagenes = self.vault_path / inp.get("imagenes", "03_Materiales\\Imagenes")
        self.input_pdfs = self.vault_path / inp.get("pdfs", "03_Materiales\\PDFs")

        # -- Output paths (relativos al vault) --
        out = self._raw.get("output", {})
        self.output_transcripts = self.vault_path / out.get(
            "transcripts", "04_Procesados\\Transcripts"
        )
        self.output_audios_tts = self.vault_path / out.get(
            "audios_tts", "04_Procesados\\AudiosTTS"
        )
        self.output_metadata = self.vault_path / out.get(
            "metadata", "04_Procesados\\Metadata"
        )

        # -- Tools: FFmpeg --
        tools = self._raw.get("tools", {})
        ffmpeg = tools.get("ffmpeg", {})
        self.ffmpeg_exe = self._resolve_path(
            ffmpeg.get("exe", "tools\\ffmpeg-bin\\ffmpeg.exe"),
            base_dir=self.config_path.parent,
        )
        self.ffprobe_exe = self._resolve_path(
            ffmpeg.get("ffprobe", "tools\\ffmpeg-bin\\ffprobe.exe"),
            base_dir=self.config_path.parent,
        )

        # -- Tools: Piper --
        piper = tools.get("piper", {})
        self.piper_exe = self._resolve_path(
            piper.get("exe", "tools\\piper\\piper.exe"),
            base_dir=self.config_path.parent,
        )
        self.piper_model = self._resolve_path(
            piper.get("model", "tools\\voices\\es_ES-mls_10246-low.onnx"),
            base_dir=self.config_path.parent,
        )
        self.piper_config = (
            self._resolve_path(piper.get("config", ""), base_dir=self.config_path.parent)
            if piper.get("config")
            else None
        )
        self.piper_speaker = piper.get("speaker", 0)
        self.piper_length_scale = piper.get("length_scale", 1.0)
        self.piper_sentence_silence = piper.get("sentence_silence", 0.3)

        # -- LLM --
        llm = self._raw.get("llm", {})
        self.llm_provider = llm.get("provider", "ollama")
        self.llm_model = llm.get("model", "gemma4:e4b")
        self.llm_endpoint = llm.get("endpoint", "http://localhost:11434")
        self.llm_temperature = llm.get("temperature", 0.7)
        self.llm_max_tokens = llm.get("max_tokens", 4096)
        self.llm_timeout = llm.get("timeout", 120)

        # -- Transcription --
        trans = self._raw.get("transcription", {})
        self.whisper_model_size = trans.get("model_size", "base")
        self.whisper_device = trans.get("device", "cpu")
        self.whisper_compute_type = trans.get("compute_type", "int8")
        self.whisper_language = trans.get("language", "es")
        self.whisper_timestamps = trans.get("timestamps", True)
        self.whisper_beam_size = trans.get("beam_size", 5)

        # -- University --
        uni = self._raw.get("university", {})
        self.current_cycle = uni.get("current_cycle", "2026-I")
        self.total_weeks = uni.get("total_weeks", 16)
        self.courses = [CourseConfig(c) for c in uni.get("courses", [])]

        # -- Watcher --
        watcher = self._raw.get("watcher", {})
        self.watcher_enabled = watcher.get("enabled", False)
        self.watcher_poll_interval = watcher.get("poll_interval", 5)
        self.watcher_extensions = set(watcher.get("watch_extensions", []))

        # -- Logging --
        log_cfg = self._raw.get("logging", {})
        self.log_level = log_cfg.get("level", "INFO")
        self.log_console = log_cfg.get("console", True)

        # Resolver ruta de log (relativa al proyecto)
        log_file = log_cfg.get("file", "logs\\academia.log")
        if not Path(log_file).is_absolute():
            self.log_file = self.config_path.parent / log_file
        else:
            self.log_file = Path(log_file)

    def get_course(self, course_id: str) -> Optional[CourseConfig]:
        """Busca un curso por su ID."""
        for course in self.courses:
            if course.id == course_id:
                return course
        return None

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Accede a un valor anidado usando notación de punto.
        Ejemplo: settings.get("llm.model") → "gemma4:e4b"
        """
        keys = key_path.split(".")
        value = self._raw
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value

    def __repr__(self) -> str:
        return f"Settings(vault={self.vault_path}, llm={self.llm_model})"


def load_settings(config_path: Optional[Path] = None) -> Settings:
    """
    Carga la configuración global (Singleton).
    La primera llamada inicializa; las siguientes retornan la misma instancia.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Settings(config_path)

        # Inicializar logger con la configuración cargada
        setup_logger(
            name="academia",
            level=_config_instance.log_level,
            log_file=str(_config_instance.log_file),
            console=_config_instance.log_console,
        )

    return _config_instance


def get_settings() -> Settings:
    """Obtiene la instancia de configuración. Debe haberse llamado load_settings antes."""
    if _config_instance is None:
        return load_settings()
    return _config_instance
