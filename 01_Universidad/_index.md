---
tipo: indice
fecha: 2026-04-15
tags:
  - indice
  - universidad
---

# 📚 Universidad — Cursos Activos

> Cada curso se crea dentro de su ciclo y las semanas, sesiones y tareas heredan esa ruta.

## ⚡ Acciones rápidas

> [!NOTE] 🚀 Clic para crear:
> - 🏫 **[Nuevo Curso](obsidian://quickadd?choice=%F0%9F%8F%AB%20Nuevo%20Curso%20Universitario)**
> - 📅 **[Nueva Semana](obsidian://quickadd?choice=%F0%9F%93%85%20Nueva%20Semana)**
> - 📖 **[Sesión Teoría](obsidian://quickadd?choice=%F0%9F%93%96%20Sesi%C3%B3n%20de%20Teor%C3%ADa)**
> - 🔧 **[Sesión Práctica](obsidian://quickadd?choice=%F0%9F%94%A7%20Sesi%C3%B3n%20de%20Pr%C3%A1ctica)**
> - 📋 **[Nueva Tarea](obsidian://quickadd?choice=%F0%9F%93%8B%20Nueva%20Tarea)**

---

## 📖 Mis cursos

```dataview
TABLE WITHOUT ID
  link(file.link, curso_nombre) AS "📖 Curso",
  ciclo AS "Ciclo",
  estado AS "Estado",
  fecha_inicio AS "Inicio"
FROM "01_Universidad"
WHERE tipo = "curso"
SORT ciclo ASC, curso_nombre ASC
```

---

## 📅 Sesiones recientes

```dataview
TABLE WITHOUT ID
  link(file.link, curso_nombre) AS "Curso",
  ciclo AS "Ciclo",
  semana AS "Semana",
  sesion AS "Tipo",
  estado AS "Estado"
FROM "01_Universidad"
WHERE tipo = "sesion"
SORT fecha DESC
LIMIT 20
```

---

## 📊 Progreso por curso

```dataview
TABLE WITHOUT ID
  curso_nombre AS "Curso",
  length(rows) AS "Sesiones registradas"
FROM "01_Universidad"
WHERE tipo = "sesion"
GROUP BY curso_nombre
SORT curso_nombre ASC
```

---

## 🔙 Navegación

- [[00_Dashboard/Dashboard|⬅️ Dashboard]]
- [[02_Coursera/_index|🌐 Coursera]]

