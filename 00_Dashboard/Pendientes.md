---
tipo: pendientes
fecha: 2026-04-15
tags:
  - dashboard
  - tareas
---

# ✅ Pendientes

> Vista consolidada de todas las tareas activas.
> **Fecha:** `= date(now)`

---

## 🔴 Tareas por entregar (próximas)

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

## ✅ Checklist global

```dataview
TASK
FROM "01_Universidad" OR "02_Coursera"
WHERE !completed
GROUP BY file.folder
```

---

## 📊 Tareas completadas

```dataview
TABLE WITHOUT ID
  link(file.link, titulo) AS "✅ Tarea",
  curso_nombre AS "Curso",
  ciclo AS "Ciclo",
  calificacion AS "Nota",
  fecha_entrega AS "Entregada"
FROM "01_Universidad"
WHERE tipo = "tarea" AND (estado = "completado" OR estado = "entregado")
SORT fecha_entrega DESC
LIMIT 10
```

---

## 🔙 [[00_Dashboard/Dashboard|⬅️ Dashboard]]
