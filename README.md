# ObsidianPersonal

Vault personal de Obsidian para flujo académico (Universidad + Coursera), con automatizaciones locales en Linux/Windows.

## Estructura principal

- `00_Dashboard`: paneles y seguimiento
- `01_Universidad`: cursos, semanas, sesiones
- `02_Coursera`: programas, cursos, módulos, lecciones
- `03_Materiales`: entradas (audio/video/imágenes/pdf)
- `04_Procesados`: salidas procesadas
- `05_Plantillas`: templates de notas
- `06_Sistema`: documentación, scripts y backend (`ObsidianAcademia`)

## Requisitos base

- Obsidian + plugins comunitarios (QuickAdd, Templater, Dataview, Buttons, Excalidraw)
- Python 3
- Node.js (si usas scripts JS del vault)
- En Linux:
  - Syncthing para sincronización multi-dispositivo
  - Piper (TTS) nativo Linux
  - Ollama para LLM local

## Validación rápida

Desde la raíz del vault:

```bash
python3 06_Sistema/scripts/validate_obsidian_postcopy.py
```

Backend completo:

```bash
python3 06_Sistema/ObsidianAcademia/main.py validate
```

## Manuales

- `06_Sistema/Manuales/Manual_Sync_Linux_Windows_Android_y_Ajustes_CrossPlatform.md`
- `06_Sistema/Manuales/Linux/Manual_Linux_Syncthing_Piper_Ollama_Gemma.md`
- `06_Sistema/Manuales/Linux/Manual_Publicacion_GitHub_ObsidianPersonal.md`
