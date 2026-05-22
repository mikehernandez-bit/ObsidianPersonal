---
tipo: sistema
fecha: 2026-05-16
tags:
  - sistema
  - instalacion
  - reproducibilidad
---

# Reproducir el sistema completo

Esta nota explica qué ya viaja dentro del vault y qué todavía depende de la
máquina. El objetivo es que puedas copiar `Personal` a otra PC y volver a dejar
funcionando Obsidian, QuickAdd, Gemma 4 Vision, Piper y el pipeline de
Coursera con el menor trabajo manual posible.

> [!info] Estado actual
> El backend local ya vive dentro de `06_Sistema/ObsidianAcademia`.
> QuickAdd y los helpers de Coursera ya buscan primero esa copia local.

## Qué está dentro de `Personal`

Todo esto ya está dentro del vault:

- `01_Universidad`, `02_Coursera`, `05_Plantillas` y `06_Sistema`
- `.obsidian` con la configuración de QuickAdd, Templater y botones
- `06_Sistema/scripts/coursera_lesson_actions.py`
- `06_Sistema/scripts/quickadd_coursera_lesson_actions.js`
- `06_Sistema/ObsidianAcademia` con `src`, `main.py`, `config.yaml`,
  `requirements.txt` e `install.ps1`
- `06_Sistema/ObsidianAcademia/tools/piper`
- `06_Sistema/ObsidianAcademia/tools/voices`

## Qué sigue siendo externo

Estas piezas no viajan de forma garantizada solo por copiar el vault:

- **Python** instalado en Windows
- **Ollama** instalado y operativo
- el modelo `gemma4:e4b` descargado en Ollama
- **Tesseract OCR**, solo si quieres fallback OCR además de Gemma Vision
- **FFmpeg**, si todavía no ejecutaste el instalador local en la nueva máquina

> [!note]
> Las imágenes ya usan Gemma 4 en modo visión real. Tesseract queda como
> fallback, no como camino principal.

## Instalación rápida en otra PC

Después de copiar la carpeta `Personal`, abre PowerShell y ejecuta:

```powershell
cd C:\ruta\de\Personal\06_Sistema
.\Instalar_Sistema_Completo.ps1
```

Ese script hace esto:

1. Usa el backend local `06_Sistema\ObsidianAcademia`.
2. Descarga `ffmpeg` dentro de `06_Sistema\ObsidianAcademia\tools`.
3. Descarga `piper.exe` dentro de `06_Sistema\ObsidianAcademia\tools\piper`.
4. Descarga la voz `es_ES-mls_10246-low` dentro de
   `06_Sistema\ObsidianAcademia\tools\voices`.
5. Crea `.venv` dentro de `06_Sistema\ObsidianAcademia`.
6. Instala las dependencias Python del proyecto.
7. Intenta dejar listo `gemma4:e4b` en Ollama.
8. Ejecuta una validación final.

## Validación

Si quieres validar sin reinstalar todo:

```powershell
cd C:\ruta\de\Personal\06_Sistema
.\Validar_Sistema_Completo.ps1
```

Si quieres validar especificamente el vault y los plugins:

```powershell
cd C:\ruta\de\Personal\06_Sistema
.\Verificar_Obsidian_Post_Copia.ps1
```

También puedes validar el backend directamente:

```powershell
cd C:\ruta\de\Personal\06_Sistema\ObsidianAcademia
.\.venv\Scripts\python.exe .\main.py validate
```

## Rutas portables

El backend local ahora usa rutas relativas:

- el `vault.path` de `config.yaml` apunta a `..\..`
- `ffmpeg`, `piper` y la voz se resuelven desde `tools\...`
- QuickAdd busca primero `06_Sistema/ObsidianAcademia`

Eso significa que ya no dependes de `C:\Users\jhoan\ObsidianAcademia` para que
los botones de Coursera funcionen.

## Lo que debes revisar después de moverlo

Haz estas comprobaciones en Obsidian:

1. Abre una lección de Coursera.
2. Ejecuta `Procesar leccion completa` o `Generar informe`.
3. Confirma que el resultado aparezca dentro de la misma carpeta de la lección.
4. Revisa que `L1.md` o la nota equivalente muestre los embeds actualizados.

Si algo falla, revisa primero:

- `06_Sistema/ObsidianAcademia/config.yaml`
- `06_Sistema/ObsidianAcademia/logs/academia.log`
- el estado de `ollama list`
- si `.\Validar_Sistema_Completo.ps1` pasa limpio
- si `.\Verificar_Obsidian_Post_Copia.ps1` pasa limpio

## Siguiente paso

Si quieres que esto quede todavía más portable, el siguiente salto lógico es
añadir un exportador o empaquetador que genere un bundle único para otra máquina
con checklist de instalación y prueba automática.
