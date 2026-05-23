# Contexto Maestro

## Perfil
- Nombre: Mike (jhoan / Mike Hernandez)
- Objetivo principal: Operar un vault de Obsidian académico/productivo con automatizaciones estables en entorno dual boot (Linux + Windows) y sincronización móvil.
- Objetivos secundarios:
  - Mantener documentación técnica replicable dentro del vault.
  - Tener backend local IA funcional (Piper + Ollama) sin romper compatibilidad cross-platform.
  - Publicar y versionar el vault en GitHub con buenas prácticas de exclusión de binarios/artefactos.

## Proyectos activos
- Proyecto: ObsidianPersonal (vault principal)
  - Rutas relevantes:
    - Ruta original (partición Windows): `/run/media/mike/Acer/Users/jhoan/Documents/Obsidian/Personal`
    - Ruta Linux nativa de prueba: `/home/mike/ObsidianVaults/Personal`
  - Estado: Sistema funcional en organización/sincronización/automatizaciones base; incidencia crítica de visualización PDF dentro de Obsidian (`0 de 0`) acotada a problema de renderer/paquete en Linux.
  - Stack:
    - Obsidian + plugins (QuickAdd, Templater, Dataview, Buttons, Excalidraw)
    - Python scripts + backend `ObsidianAcademia`
    - Node scripts auxiliares
    - Syncthing (Linux/Windows/Android)
    - Ollama local + Piper TTS
  - Decisiones vigentes:
    - Binarios/runtime por SO fuera del vault (`~/.local/bin`, `~/.local/lib`, servicios systemd --user).
    - Contenido/markdown/config/scripts del proyecto dentro del vault.
    - Rutas y validaciones cross-platform priorizando Linux nativo cuando se detecten `.exe`.

## Preferencias de trabajo con IA
- Idioma: Español
- Nivel técnico esperado: Alto, con explicación clara y accionable.
- Estilo de respuesta: Directo, práctico, sin relleno, pasos concretos.
- Restricciones (tools, formatos, etc):
  - Documentar cambios en Markdown dentro de `06_Sistema/Manuales`.
  - Mantener nombres de manuales descriptivos (no demasiado largos ni ambiguos).
  - Evitar soluciones que rompan sincronización entre Linux/Windows/Android.

## Reglas personales
- Todo cambio importante debe quedar registrado en manual o registro.
- Priorizar estabilidad de sincronización (Syncthing) antes de cambios grandes de backend.
- Mantener compatibilidad dual boot (Windows y Linux) en configuración y flujo.

## Estado técnico actual
- Persistencia:
  - Sistema de memoria persistente activo en `06_Sistema/AI_Persistente`.
  - Registros de sesión y cambios mantenidos.
- Syncthing:
  - Linux configurado como nodo activo en malla Linux + Windows + Celular.
  - Servicio activo y validado por API.
  - Conflictos iniciales y elemento no sincronizado corregidos.
- Estructura académica semanal:
  - Todas las semanas existentes tienen carpeta `Material`.
  - Flujos de creación de semana ajustados para crear `Material` automáticamente.
  - Se evitó subestructura fija dentro de `Material` por indicación de flujo real.
- Plantillas/Notas de sesión:
  - Plantillas de teoría y práctica actualizadas a formato de captura rápida:
    - `## Notas`
    - `### Informacion`
    - `### Preguntas`
  - Sesiones ya creadas migradas a esta estructura.
- Backend ObsidianAcademia:
  - `ffmpeg` y `ffprobe` con fallback Linux nativo.
  - `piper` nativo Linux instalado/validado.
  - `ollama` como servicio user y modelo `gemma4:e4b` descargado.
- Manuales:
  - Manuales actualizados y renombrados en `06_Sistema/Manuales` y `06_Sistema/Manuales/Linux`.
- Git:
  - Repo local inicializado y commit base creado.
  - Remoto GitHub configurado.
  - Push pendiente por autenticación.

## Dudas finales abiertas
- PDF en Obsidian sigue mostrando `0 de 0` incluso después de:
  - reset de workspace,
  - desactivación de plugins comunitarios,
  - normalización de PDF con `qpdf --linearize`,
  - limpieza de cachés de Obsidian,
  - arranque con `--disable-gpu --disable-gpu-compositing`,
  - prueba en vault copiado a ruta Linux nativa,
  - prueba con Obsidian AppImage `1.12.7`,
  - prueba con Obsidian AppImage `1.11.5`,
  - prueba con flags `--ozone-platform=x11 --disable-gpu`.
- Hipótesis técnica consolidada: incompatibilidad del renderer PDF de Obsidian con el entorno gráfico Linux actual (no aislada a una sola versión/paquete).
- Decisión operativa vigente: abrir PDF siempre en aplicación externa del sistema.

## Pendientes globales
- [ ] Mantener política de operación: PDF siempre en app externa mientras persista `0 de 0` en Obsidian.
- [ ] Definir ruta final de trabajo del vault (preferencia: Linux nativo + Syncthing estable).
- [ ] Completar autenticación GitHub en esta máquina (`gh auth login`).
- [ ] Ejecutar push final a `origin/main` del repositorio `ObsidianPersonal`.
- [ ] Ejecutar validación final de backend (`python3 06_Sistema/ObsidianAcademia/main.py validate`) y registrar resultado final.
- [ ] Revisar y mantener actualizado este Contexto Maestro en cada cierre relevante.
