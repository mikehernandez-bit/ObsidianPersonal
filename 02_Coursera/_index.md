---
tipo: indice
fecha: 2026-04-15
tags:
  - indice
  - coursera
---

# 🌐 Coursera

## ⚡ Acciones rápidas

> [!NOTE] 🚀 Clic para crear:
> - 🎓 **[Nuevo Programa](obsidian://quickadd?choice=%F0%9F%8E%93%20Nuevo%20Programa%20Coursera)** 
> - 📚 **[Nuevo Curso](obsidian://quickadd?choice=%F0%9F%93%9A%20Nuevo%20Curso%20Coursera)** 
> - 📦 **[Nuevo Módulo](obsidian://quickadd?choice=%F0%9F%93%A6%20Nuevo%20M%C3%B3dulo%20Coursera)** 
> - 📝 **[Nueva Lección](obsidian://quickadd?choice=%F0%9F%93%9D%20Nueva%20Lecci%C3%B3n%20Coursera)** 

---

## 🎓 Programas (Especializaciones)

```dataview
TABLE WITHOUT ID
  link(file.link, programa) AS "🎓 Programa",
  estado AS "Estado",
  fecha_inicio AS "Inicio"
FROM "02_Coursera"
WHERE tipo = "programa_coursera"
SORT programa ASC
```

---

## 📚 Cursos activos

```dataview
TABLE WITHOUT ID
  link(file.link, curso) AS "📚 Curso",
  programa AS "Programa",
  estado AS "Estado",
  fecha_inicio AS "Inicio"
FROM "02_Coursera"
WHERE tipo = "curso_coursera"
SORT curso ASC
```

---

## 📦 Módulos en progreso

```dataview
TABLE WITHOUT ID
  link(file.link, modulo) AS "📦 Módulo",
  curso AS "Curso",
  estado AS "Estado"
FROM "02_Coursera"
WHERE tipo = "modulo_coursera" AND estado = "en_curso"
SORT curso ASC, modulo ASC
```

---

## 📝 Últimas lecciones

```dataview
TABLE WITHOUT ID
  link(file.link, leccion) AS "📝 Lección",
  curso AS "Curso",
  modulo AS "Módulo",
  estado AS "Estado",
  fecha AS "Fecha"
FROM "02_Coursera"
WHERE tipo = "leccion_coursera"
SORT fecha DESC
LIMIT 15
```

---

## 📋 Resúmenes Coursera

```dataview
LIST
FROM "02_Coursera"
WHERE tipo = "resumen"
SORT fecha DESC
LIMIT 10
```

---

## 🔙 Navegación

- [[00_Dashboard/Dashboard|⬅️ Dashboard]]
- [[01_Universidad/_index|📚 Universidad]]
