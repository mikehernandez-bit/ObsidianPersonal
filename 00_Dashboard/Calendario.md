---
tipo: calendario
fecha: 2026-04-15
tags:
  - dashboard
  - calendario
---

# 📅 Calendario Semanal

> Vista de actividades por semana.

---

## 📌 Esta semana

```dataview
TABLE WITHOUT ID
  link(file.link, file.name) AS "📝 Nota",
  tipo AS "Tipo",
  curso_nombre AS "Curso",
  ciclo AS "Ciclo",
  sesion AS "Sesión",
  estado AS "Estado"
FROM "01_Universidad" OR "02_Coursera"
WHERE fecha >= date(today) - dur(7 days) AND fecha <= date(today) + dur(1 day)
SORT fecha DESC
```

---

## 📅 Entregas próximas (7 días)

```dataview
TABLE WITHOUT ID
  link(file.link, titulo) AS "📋 Tarea",
  curso_nombre AS "Curso",
  ciclo AS "Ciclo",
  fecha_entrega AS "📅 Entrega"
FROM "01_Universidad"
WHERE tipo = "tarea" AND estado != "completado" AND fecha_entrega <= date(today) + dur(7 days)
SORT fecha_entrega ASC
```

---

## 📊 Actividad de las últimas 2 semanas

```dataview
TABLE WITHOUT ID
  link(file.link, file.name) AS "Archivo",
  tipo AS "Tipo",
  fecha AS "Fecha"
FROM "01_Universidad" OR "02_Coursera"
WHERE fecha >= date(today) - dur(14 days)
SORT fecha DESC
LIMIT 30
```

---

## 🔙 [[00_Dashboard/Dashboard|⬅️ Dashboard]]
