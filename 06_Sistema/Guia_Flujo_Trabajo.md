---
tipo: guia
fecha: 2026-04-15
tags:
  - sistema
  - guia
  - flujo
---

# 📘 Guía de Flujo de Trabajo — ObsidianAcademia

> Todo se hace con **botones** desde Obsidian. No necesitas la terminal para crear notas.

---

## 📑 Índice

1. [[#🏫 Añadir un nuevo curso universitario]]
2. [[#📅 Iniciar una nueva semana]]
3. [[#📖 Registrar sesión de Teoría]]
4. [[#🔧 Registrar sesión de Práctica]]
5. [[#📋 Crear una tarea]]
6. [[#🌐 Coursera — Nuevo programa]]
7. [[#📚 Coursera — Nuevo curso]]
8. [[#📦 Coursera — Nuevo módulo]]
9. [[#📝 Coursera — Nueva lección]]
10. [[#🤖 Procesar material con IA]]
11. [[#👁️ Monitoreo automático]]
12. [[#📐 Diagrama del flujo completo]]

---

# 🏫 Añadir un nuevo curso universitario

> **Ejemplo:** Quieres añadir "Robótica" (código RB901)

### Paso a paso

```button
name 🏫 Crear nuevo curso ahora
type command
action QuickAdd: Run QuickAdd
color blue
```

1. **Haz clic en el botón** de arriba (o ve al Dashboard y haz clic en "🏫 Nuevo Curso")
2. QuickAdd te muestra las acciones → selecciona **"🏫 Nuevo Curso Universitario"**
3. Te pide un **nombre para la nota** → escribe: `Curso_robotica/_curso`
4. La plantilla se aplica automáticamente y te pregunta:
   - **ID del curso:** `robotica`
   - **Nombre del curso:** `Robótica`
   - **Código del curso:** `RB901`
5. ✅ ¡Listo! Se crea la nota con todas las queries de Dataview

### Para crear las 16 semanas automáticamente (terminal):

```powershell
cd C:\ruta\de\Personal\06_Sistema\ObsidianAcademia
.venv\Scripts\Activate.ps1
python main.py init-course --name "Robótica" --code "RB901"
```

> [!TIP] ¿Cuándo usar botón vs terminal?
> - **Botón:** Para crear la nota rápida del curso en cualquier momento
> - **Terminal:** Para crear el curso + las 16 semanas con carpetas Teoria/Practica de una vez (recomendado al inicio del ciclo)

---

# 📅 Iniciar una nueva semana

```button
name 📅 Crear nueva semana
type command
action QuickAdd: Run QuickAdd
color purple
```

1. Clic en el botón → selecciona **"📅 Nueva Semana"**
2. Te pide seleccionar la **carpeta de destino** → navega a `01_Universidad/Curso_robotica/Semana_05/`
3. Nombre de la nota: `_semana`
4. Llena: curso, nombre, semana

---

# 📖 Registrar sesión de Teoría

> **Ejemplo:** Hoy tienes clase teórica de Robótica, Semana 5

```button
name 📖 Crear sesión de Teoría
type command
action QuickAdd: Run QuickAdd
color green
```

### Antes de la clase
1. Clic en el botón → selecciona **"📖 Sesión de Teoría"**
2. Carpeta destino: `01_Universidad/Curso_robotica/Semana_05/Teoria/`
3. Nombre: `sesion`
4. Llena: ID curso → `robotica`, nombre → `Robótica`, semana → `5`

### Durante la clase
- ✏️ Toma notas en la sección "Notas de clase"
- 🎙️ **Graba audio** con Super Duper Audio Recorder (ya instalado en Obsidian)
- 📸 Toma fotos de la pizarra → arrástralas a la nota
- ❓ Anota preguntas que surjan

### Después de la clase  — procesar con IA
```powershell
python main.py process-session --curso robotica --semana 5 --tipo Teoria ^
  --files "C:\ruta\audio_clase.mp3" --files "C:\ruta\foto_pizarra.jpg"
```

### ¿Qué se genera?

| 📄 Archivo | 📝 Contenido |
|---|---|
| `transcript.md` | Transcripción completa del audio |
| `resumen.md` | Resumen estructurado (IA) |
| `cuestionario.md` | Quiz de 8 preguntas con respuestas |
| `informe.md` | Informe formal de la sesión |
| `puntos_clave.md` | Los 5-10 puntos más importantes |
| `dudas.md` | Preguntas que deberías resolver |
| `proximas_acciones.md` | Tareas de estudio sugeridas |
| `audio_script.md` | Guion del audio explicativo |
| `audio_explicativo.wav` | 🔊 Audio para repasar escuchando |

Todos estos archivos aparecen como links `[[archivo]]` en tu nota de sesión.

---

# 🔧 Registrar sesión de Práctica

```button
name 🔧 Crear sesión de Práctica
type command
action QuickAdd: Run QuickAdd
color green
```

Igual que Teoría, pero:
- Selecciona **"🔧 Sesión de Práctica"** en QuickAdd
- Carpeta destino: `Practica/` en vez de `Teoria/`
- Terminal: usa `--tipo Practica`

---

# 📋 Crear una tarea

```button
name 📋 Crear tarea
type command
action QuickAdd: Run QuickAdd
color yellow
```

1. Clic en el botón → **"📋 Nueva Tarea"**
2. Carpeta destino: `01_Universidad/Curso_robotica/Tareas/` (o cualquier carpeta del curso)
3. Nombre: `Diseño brazo robótico` (el título de la tarea)
4. La plantilla te pregunta: curso, nombre del curso, título, fecha de entrega

La tarea aparecerá automáticamente en:
- ✅ **Dashboard** → sección "Tareas pendientes"
- 📋 **Nota del curso** → sección "Tareas"
- 📅 **Calendario** → si tiene fecha de entrega

---

# 🌐 Coursera — Nuevo programa

> **Ejemplo:** Programa "Deep Learning" de Andrew Ng

```button
name 🎓 Crear programa Coursera
type command
action QuickAdd: Run QuickAdd
color red
```

1. Clic en el botón → **"🎓 Nuevo Programa Coursera"**
2. Nombre de la nota: `Programa_Deep_Learning/_programa`
3. Llena: Nombre del programa → `Deep Learning`

### Estructura que se crea:
```
02_Coursera/
└── Programa_Deep_Learning/
    └── _programa.md    ← Con Dataview que lista cursos del programa
```

---

# 📚 Coursera — Nuevo curso

> **Ejemplo:** Curso "Neural Networks" dentro del programa Deep Learning

```button
name 📚 Crear curso Coursera
type command
action QuickAdd: Run QuickAdd
color blue
```

1. Clic en el botón → **"📚 Nuevo Curso Coursera"**
2. Carpeta destino: `02_Coursera/Programa_Deep_Learning/`
3. Nombre: `Curso_Neural_Networks/_curso`
4. Llena: curso, programa (o vacío si es curso suelto)

### Para un curso individual SIN programa:
- Mismo proceso, pero el programa lo dejas vacío
- Carpeta destino: directamente `02_Coursera/`

---

# 📦 Coursera — Nuevo módulo

```button
name 📦 Crear módulo Coursera
type command
action QuickAdd: Run QuickAdd
color green
```

1. Clic → **"📦 Nuevo Módulo Coursera"**
2. Carpeta destino: `02_Coursera/Programa_Deep_Learning/Curso_Neural_Networks/`
3. Nombre: `Modulo_01_Introduccion/_modulo`
4. Llena: curso, módulo, programa

---

# 📝 Coursera — Nueva lección

```button
name 📝 Crear lección Coursera
type command
action QuickAdd: Run QuickAdd
color yellow
```

1. Clic → **"📝 Nueva Lección Coursera"**
2. Carpeta destino: `02_Coursera/.../Modulo_01_Introduccion/`
3. Nombre: `Leccion_01_Que_es_NN`
4. Llena: curso, módulo, lección, programa

### Procesar video de la lección con IA:
```powershell
python main.py process-coursera ^
  --course "Neural Networks and Deep Learning" ^
  --module "01 Introduccion" ^
  --lesson "Que es una red neuronal" ^
  --program "Deep Learning" ^
  --files "C:\ruta\leccion_video.mp4"
```

---

# 🤖 Procesar material con IA

> Esto se hace desde la terminal. El procesamiento toma varios minutos porque transcribe audio, genera 7 productos con IA y crea audio TTS.

### Comandos por tipo de material

| Qué quieres procesar | Comando |
|---|---|
| 🎙️ Audio de clase | `python main.py process-audio "audio.mp3" --curso X --semana N --tipo Teoria` |
| 📹 Video de clase | `python main.py process-video "video.mp4" --curso X --semana N --tipo Teoria` |
| 📸 Foto de pizarra | `python main.py process-image "foto.jpg" --curso X --semana N` |
| 📁 Sesión completa | `python main.py process-session --curso X --semana N --tipo Teoria --dir ./carpeta` |
| 🌐 Lección Coursera | `python main.py process-coursera -c "Curso" -m "Mod" -l "Lec" --files video.mp4` |
| 🚫 Sin audio TTS | Añade `--no-tts` a cualquier comando |

### Flujo interno del procesamiento

```
📥 Tu archivo (audio/video/imagen/PDF)
    ↓
🔊 Video → extrae audio (FFmpeg)
    ↓
📝 Audio → transcripción (faster-whisper, local)
    ↓
🖼️ Imagen → extrae texto (OCR)
    ↓
📄 PDF → extrae texto (PyMuPDF)
    ↓
🔗 Consolida todo el contenido
    ↓
🤖 Gemma 4 E4B (Ollama, local) → genera 7 productos
    ↓
🎙️ Texto → Audio explicativo (Piper TTS, local)
    ↓
💾 Todo guardado en la carpeta de la sesión
```

---

# 👁️ Monitoreo automático (Watcher)

```powershell
python main.py watch
```

Monitorea estas carpetas y procesa automáticamente:
- `03_Materiales/Audios/` → procesa audios
- `03_Materiales/Videos/` → procesa videos
- `03_Materiales/Imagenes/` → procesa imágenes

**Flujo:**
1. Deja `watch` corriendo en terminal
2. Copia archivos a `03_Materiales/`
3. Se procesan automáticamente
4. Resultados en `04_Procesados/`

> [!WARNING] El watcher no sabe a qué curso/semana pertenece el archivo. Para eso usa `process-session` con los parámetros `--curso` y `--semana`.

---

# 📐 Diagrama del flujo completo

```
╔═══════════════════════════════════════════════════════╗
║              INICIO DEL CICLO (1 vez)                 ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  Terminal: python main.py init-course --all           ║
║  → Crea 6 cursos × 16 semanas                        ║
║  → O usa el botón 🏫 para cada curso                 ║
║                                                       ║
╠═══════════════════════════════════════════════════════╣
║              CADA CLASE (repetir)                     ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  1. ANTES: Clic botón 📖/🔧 → crea nota de sesión   ║
║  2. DURANTE: Toma notas + graba audio + fotos         ║
║  3. DESPUÉS: Terminal process-session → genera todo   ║
║  4. ESTUDIO: Leer resumen, hacer quiz, oír audio     ║
║                                                       ║
╠═══════════════════════════════════════════════════════╣
║              TAREAS (cuando las asignen)              ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  Clic botón 📋 → llena datos → aparece en Dashboard  ║
║                                                       ║
╠═══════════════════════════════════════════════════════╣
║              COURSERA (cuando estudies)               ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  1. Botón 🎓 → programa (1 vez por especialización)  ║
║  2. Botón 📚 → curso (1 vez por curso)               ║
║  3. Botón 📦 → módulo (1 vez por módulo)             ║
║  4. Botón 📝 → lección (cada lección)                ║
║  5. Terminal process-coursera → genera materiales     ║
║                                                       ║
╠═══════════════════════════════════════════════════════╣
║              DASHBOARD (revísalo seguido)             ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  → Tareas pendientes con fechas                       ║
║  → Sesiones recientes de todos los cursos             ║
║  → Cuestionarios para repasar                         ║
║  → Dudas sin resolver                                 ║
║  → Progreso de Coursera                               ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
```

---

## ❓ Preguntas frecuentes

### ¿Necesito la terminal para crear notas?
**No.** Todo se crea con botones desde Obsidian. La terminal solo se usa para **procesar material con IA** (transcribir, resumir, generar quizzes).

### ¿Necesito internet?
**No.** Todo es 100% local: IA (Gemma 4), transcripción (faster-whisper), audio (Piper).

### ¿Puedo crear un curso Coursera sin programa?
**Sí.** Cuando te pregunte "Programa", déjalo vacío.

### ¿Cuánto tarda procesar un audio de 1 hora?
- Transcripción: ~10-20 min (CPU)
- IA (7 productos): ~15-30 min
- TTS: ~2-5 min
- **Total: ~30-55 min** (se ejecuta en segundo plano)

### ¿Los botones funcionan en móvil?
Sí, si usas Obsidian Mobile con sync.

---

## 🔙 Navegación

- [[00_Dashboard/Dashboard|⬅️ Dashboard]]
- [[06_Sistema/Sistema|⚙️ Sistema]]
