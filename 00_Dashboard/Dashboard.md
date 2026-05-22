---
tipo: dashboard
fecha: 2026-04-15
cssclass: dashboard
tags:
  - dashboard
  - sistema
---

# 🎓 Dashboard Académico

> **Organizacion:** cursos por ciclo | **Semanas objetivo:** 16
> **Hoy:** `= date(now)`

---

## ⚡ Acciones rápidas — Universidad

> [!NOTE] 🚀 Clic para crear:
> - 🏫 **[Nuevo Curso](obsidian://quickadd?choice=%F0%9F%8F%AB%20Nuevo%20Curso%20Universitario)**  — Inicia una nueva materia
> - 📅 **[Nueva Semana](obsidian://quickadd?choice=%F0%9F%93%85%20Nueva%20Semana)** — Crea la vista semanal de un curso
> - 📖 **[Sesión Teoría](obsidian://quickadd?choice=%F0%9F%93%96%20Sesi%C3%B3n%20de%20Teor%C3%ADa)** — Clase téorica
> - 🔧 **[Sesión Práctica](obsidian://quickadd?choice=%F0%9F%94%A7%20Sesi%C3%B3n%20de%20Pr%C3%A1ctica)** — Clase práctica
> - 📋 **[Nueva Tarea](obsidian://quickadd?choice=%F0%9F%93%8B%20Nueva%20Tarea)** — Registra un pendiente

---

## ⚡ Acciones rápidas — Coursera

> [!NOTE] 🚀 Clic para crear:
> - 🎓 **[Nuevo Programa](obsidian://quickadd?choice=%F0%9F%8E%93%20Nuevo%20Programa%20Coursera)** — Especialización nueva
> - 📚 **[Nuevo Curso](obsidian://quickadd?choice=%F0%9F%93%9A%20Nuevo%20Curso%20Coursera)** — Curso individual
> - 📦 **[Nuevo Módulo](obsidian://quickadd?choice=%F0%9F%93%A6%20Nuevo%20M%C3%B3dulo%20Coursera)** — Semana/Módulo
> - 📝 **[Nueva Lección](obsidian://quickadd?choice=%F0%9F%93%9D%20Nueva%20Lecci%C3%B3n%20Coursera)** — Video/Lectura


---

## 📚 Mis cursos activos

```dataview
TABLE WITHOUT ID
  link(file.link, curso_nombre) AS "📖 Curso",
  ciclo AS "Ciclo",
  estado AS "Estado"
FROM "01_Universidad"
WHERE tipo = "curso"
SORT ciclo ASC, curso_nombre ASC
```

---

## 📅 Últimas sesiones

```dataview
TABLE WITHOUT ID
  link(file.link, curso_nombre) AS "Curso",
  ciclo AS "Ciclo",
  semana AS "Sem.",
  sesion AS "Tipo",
  estado AS "Estado",
  fecha AS "Fecha"
FROM "01_Universidad"
WHERE tipo = "sesion"
SORT fecha DESC
LIMIT 15
```

---

## ✅ Tareas pendientes

> [!WARNING] ⏰ Próximas entregas

```dataview
TABLE WITHOUT ID
  link(file.link, titulo) AS "📋 Tarea",
  curso_nombre AS "Curso",
  ciclo AS "Ciclo",
  fecha_entrega AS "📅 Entrega",
  estado AS "Estado"
FROM "01_Universidad"
WHERE tipo = "tarea" AND estado != "completado" AND estado != "entregado"
SORT fecha_entrega ASC
```

---

## 📝 Checklist global

```dataview
TASK
FROM "01_Universidad" OR "02_Coursera"
WHERE !completed
GROUP BY file.folder
LIMIT 20
```

---

## 📋 Últimos resúmenes generados

```dataview
TABLE WITHOUT ID
  link(file.link, file.name) AS "📋 Resumen",
  curso_nombre AS "Curso",
  ciclo AS "Ciclo",
  semana AS "Sem.",
  fecha AS "Fecha"
FROM "01_Universidad"
WHERE tipo = "resumen"
SORT fecha DESC
LIMIT 10
```

---

## ❓ Cuestionarios de estudio

```dataview
TABLE WITHOUT ID
  link(file.link, file.name) AS "❓ Quiz",
  curso_nombre AS "Curso",
  ciclo AS "Ciclo",
  semana AS "Sem.",
  intentos AS "Intentos",
  mejor_puntaje AS "Puntaje"
FROM "01_Universidad"
WHERE tipo = "cuestionario"
SORT fecha DESC
LIMIT 10
```

---

## 🔊 Audios explicativos

```dataview
TABLE WITHOUT ID
  link(file.link, file.name) AS "🎙️ Audio",
  curso_nombre AS "Curso",
  ciclo AS "Ciclo",
  semana AS "Sem.",
  fecha AS "Fecha"
FROM "01_Universidad"
WHERE tipo = "audio_script"
SORT fecha DESC
LIMIT 10
```

---

## ❗ Dudas sin resolver

```dataview
LIST
FROM "01_Universidad"
WHERE tipo = "dudas" AND estado = "pendiente"
SORT fecha DESC
```

---

## 🌐 Coursera

```dataview
TABLE WITHOUT ID
  link(file.link, leccion) AS "📚 Lección",
  curso AS "Curso",
  modulo AS "Módulo",
  estado AS "Estado",
  fecha AS "Fecha"
FROM "02_Coursera"
WHERE tipo = "leccion_coursera"
SORT fecha DESC
LIMIT 10
```

---

## 📊 Estadísticas

> **Sesiones registradas:**
```dataview
LIST WITHOUT ID length(rows) + " sesiones"
FROM "01_Universidad"
WHERE tipo = "sesion"
GROUP BY true
```

> **Resúmenes generados:**
```dataview
LIST WITHOUT ID length(rows) + " resúmenes"
FROM "01_Universidad"
WHERE tipo = "resumen"
GROUP BY true
```

> **Cuestionarios creados:**
```dataview
LIST WITHOUT ID length(rows) + " cuestionarios"
FROM "01_Universidad"
WHERE tipo = "cuestionario"
GROUP BY true
```

---

## 🗺️ Navegación

| | |
|---|---|
| 📚 [[01_Universidad/_index\|Universidad]] | 🌐 [[02_Coursera/_index\|Coursera]] |
| ✅ [[00_Dashboard/Pendientes\|Pendientes]] | 📅 [[00_Dashboard/Calendario\|Calendario]] |
| 📄 [[05_Plantillas\|Plantillas]] | ⚙️ [[06_Sistema/Sistema\|Sistema]] |
| 📘 [[06_Sistema/Guia_Flujo_Trabajo\|Guía de Uso]] | |
