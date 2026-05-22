"""
ObsidianAcademia - Cliente LLM
Cliente HTTP para comunicación con Ollama (Gemma 4 E4B).
Soporta generación con retry y timeout configurable.
"""

import time
from pathlib import Path
from typing import Optional, Sequence

from src.config.settings import get_settings
from src.utils.logger import get_logger

log = get_logger("llm_client")


class OllamaClient:
    """Cliente para el API de Ollama."""

    def __init__(self):
        settings = get_settings()
        self.model = settings.llm_model
        self.endpoint = settings.llm_endpoint
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        self.timeout = settings.llm_timeout
        self._client = None

    def _get_client(self):
        """Obtiene o crea el cliente de Ollama (lazy loading)."""
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client(host=self.endpoint)
                log.debug(f"Cliente Ollama inicializado: {self.endpoint}")
            except ImportError:
                log.error(
                    "Paquete 'ollama' no instalado. Ejecuta: pip install ollama"
                )
                raise
        return self._client

    def _build_messages(
        self,
        prompt: str,
        system: Optional[str] = None,
        images: Optional[Sequence[str | Path]] = None,
    ) -> list[dict]:
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})

        user_message = {"role": "user", "content": prompt}
        if images:
            user_message["images"] = [str(Path(image).resolve()) for image in images]

        messages.append(user_message)
        return messages

    def _chat_once(
        self,
        messages: list[dict],
        temperature: float,
    ) -> str:
        client = self._get_client()
        response = client.chat(
            model=self.model,
            messages=messages,
            options={
                "temperature": temperature,
                "num_predict": self.max_tokens,
            },
        )
        return response.get("message", {}).get("content", "")

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_retries: int = 2,
    ) -> Optional[str]:
        """
        Genera texto usando el modelo LLM local.
        
        Args:
            prompt: Prompt del usuario.
            system: Prompt del sistema (contexto/rol).
            temperature: Override de temperatura. None para usar config.
            max_retries: Número máximo de reintentos en caso de error.
        
        Returns:
            Texto generado, o None si falla.
        """
        temp = temperature if temperature is not None else self.temperature
        messages = self._build_messages(prompt=prompt, system=system)

        for attempt in range(1, max_retries + 1):
            try:
                log.info(
                    f"Generando con {self.model} "
                    f"(temp={temp}, intento {attempt}/{max_retries})"
                )
                start_time = time.time()
                content = self._chat_once(messages=messages, temperature=temp)
                elapsed = time.time() - start_time

                if content:
                    log.info(
                        f"Generación completada: {len(content)} caracteres "
                        f"en {elapsed:.1f}s"
                    )
                    return content
                else:
                    log.warning("Respuesta vacía del modelo")
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    return None

            except Exception as e:
                log.error(f"Error en generación (intento {attempt}): {e}")
                if attempt < max_retries:
                    wait = attempt * 3
                    log.info(f"Reintentando en {wait}s...")
                    time.sleep(wait)
                else:
                    log.error("Todos los intentos fallaron")
                    return None

        return None

    def generate_with_images(
        self,
        prompt: str,
        image_paths: Sequence[str | Path],
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_retries: int = 2,
    ) -> Optional[str]:
        """
        Genera texto usando el modelo LLM local con entradas de imagen.

        Args:
            prompt: Prompt del usuario.
            image_paths: Rutas a imagenes.
            system: Prompt del sistema (contexto/rol).
            temperature: Override de temperatura. None para usar config.
            max_retries: Numero maximo de reintentos en caso de error.

        Returns:
            Texto generado, o None si falla.
        """
        if not image_paths:
            log.warning("generate_with_images llamado sin imagenes.")
            return None

        temp = temperature if temperature is not None else self.temperature
        messages = self._build_messages(
            prompt=prompt,
            system=system,
            images=image_paths,
        )

        for attempt in range(1, max_retries + 1):
            try:
                log.info(
                    f"Generando con vision en {self.model} "
                    f"(imagenes={len(image_paths)}, temp={temp}, intento {attempt}/{max_retries})"
                )
                start_time = time.time()
                content = self._chat_once(messages=messages, temperature=temp)
                elapsed = time.time() - start_time

                if content:
                    log.info(
                        f"Generacion multimodal completada: {len(content)} caracteres "
                        f"en {elapsed:.1f}s"
                    )
                    return content

                log.warning("Respuesta vacia del modelo multimodal")
                if attempt < max_retries:
                    time.sleep(2)
                    continue
                return None

            except Exception as error:
                log.error(f"Error en generacion multimodal (intento {attempt}): {error}")
                if attempt < max_retries:
                    wait = attempt * 3
                    log.info(f"Reintentando vision en {wait}s...")
                    time.sleep(wait)
                else:
                    log.error("Todos los intentos multimodales fallaron")
                    return None

        return None

    def is_available(self) -> bool:
        """Verifica si el servicio de Ollama está disponible."""
        try:
            client = self._get_client()
            client.list()
            return True
        except Exception:
            return False


# Instancia global del cliente
_client_instance: Optional[OllamaClient] = None


def get_llm_client() -> OllamaClient:
    """Obtiene la instancia singleton del cliente LLM."""
    global _client_instance
    if _client_instance is None:
        _client_instance = OllamaClient()
    return _client_instance
