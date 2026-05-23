---
tipo: sistema
fecha: 2026-04-15
tags:
  - sistema
  - config
---

# ⚙️ Sistema ObsidianAcademia

## 📁 Estructura del vault

| Carpeta          | Contenido                                |
| ---------------- | ---------------------------------------- |
| `00_Dashboard`   | Dashboard, Pendientes, Calendario        |
| `01_Universidad` | Cursos → Semanas → Sesiones + Productos  |
| `02_Coursera`    | Programas → Cursos → Módulos → Lecciones |
| `03_Materiales`  | Audio, Video, Imágenes, PDFs de entrada  |
| `04_Procesados`  | Transcripts, AudiosTTS, Metadata         |
| `05_Plantillas`  | Templates para Templater                 |
| `06_Sistema`     | Configuración, docs del sistema          |

---

## 🛠️ Comandos del sistema

### Inicialización
```bash
python main.py validate      # Validar todo
python main.py init-vault    # Crear estructura
python main.py init-course --all  # Crear cursos
```

### Procesamiento
```bash
# Audio de clase
python main.py process-audio "ruta.mp3" --curso curso_01 --semana 3 --tipo Teoria

# Video de clase
python main.py process-video "ruta.mp4" --curso curso_01 --semana 3 --tipo Practica

# Imagen (pizarra, diapositiva)
python main.py process-image "foto.jpg" --curso curso_01 --semana 3

# Sesión completa (múltiples archivos)
python main.py process-session --curso curso_01 --semana 3 --tipo Teoria --dir ./archivos

# Coursera
python main.py process-coursera -c "ML" -m "Semana 1" -l "Intro" --files video.mp4
```

### Monitoreo automático
```bash
python main.py watch    # Monitorea carpetas de entrada
python main.py status   # Estado del sistema
```

---

## 📄 Plantillas disponibles

| Plantilla | Uso | Comando Templater |
|---|---|---|
| `TPL_Curso` | Nuevo curso universitario | Ctrl+T → TPL_Curso |
| `TPL_Semana` | Nueva semana | Ctrl+T → TPL_Semana |
| `TPL_Sesion_Teoria` | Sesión de teoría | Ctrl+T → TPL_Sesion_Teoria |
| `TPL_Sesion_Practica` | Sesión de práctica | Ctrl+T → TPL_Sesion_Practica |
| `TPL_Tarea` | Nueva tarea | Ctrl+T → TPL_Tarea |
| `TPL_Coursera_Programa` | Programa de Coursera | Ctrl+T → TPL_Coursera_Programa |
| `TPL_Coursera_Curso` | Curso de Coursera | Ctrl+T → TPL_Coursera_Curso |
| `TPL_Coursera_Modulo` | Módulo de Coursera | Ctrl+T → TPL_Coursera_Modulo |
| `TPL_Coursera_Leccion` | Lección de Coursera | Ctrl+T → TPL_Coursera_Leccion |

---

## 📊 Productos que genera la IA

| Producto | Archivo | Descripción |
|---|---|---|
| Transcripción | `transcript.md` | Texto del audio/video (faster-whisper) |
| Informe | `informe.md` | Informe estructurado de la sesión |
| Resumen | `resumen.md` | Resumen de conceptos principales |
| Cuestionario | `cuestionario.md` | Quiz de estudio con respuestas |
| Puntos clave | `puntos_clave.md` | Los 5-10 puntos más importantes |
| Dudas | `dudas.md` | Preguntas pendientes identificadas |
| Próximas acciones | `proximas_acciones.md` | Tareas de estudio sugeridas |
| Guion de audio | `audio_script.md` | Texto para TTS |
| Audio explicativo | `audio_explicativo.wav` | Audio TTS generado con Piper |

---

## 🔧 Configuración

La configuración del sistema está en:
`06_Sistema/ObsidianAcademia/config.yaml`

Guia recomendada:
[[Reproducir_Sistema_Completo]]

Manuales:
[[Manuales/Linux/syncthing_linux_crossplatform]]
[[Manuales/Linux/linux_piper_ollama_gemma_setup]]

### Modelo IA
- **Modelo:** Gemma 4 E4B (via Ollama)
- **Endpoint:** http://localhost:11434

### Herramientas
- **FFmpeg:** `06_Sistema/ObsidianAcademia/tools/ffmpeg-bin`
- **Piper TTS:** `06_Sistema/ObsidianAcademia/tools/piper`
- **Voz:** es_ES-mls_10246-low

---

## 🔙 [[00_Dashboard/Dashboard|⬅️ Dashboard]]
