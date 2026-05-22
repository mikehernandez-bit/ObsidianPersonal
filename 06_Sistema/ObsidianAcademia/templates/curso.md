---
tipo: curso
id: {{ id }}
curso_nombre: "{{ curso_nombre }}"
ciclo: {{ ciclo }}
semanas_total: {{ semanas_total }}
estado: {{ estado | default("activo") }}
fecha_inicio: {{ fecha }}
tags:
  - academia
  - curso
  - {{ id }}
---

# {{ curso_nombre }}

**Ciclo:** {{ ciclo }}
**Semanas totales:** {{ semanas_total }}
**Estado:** {{ estado | default("activo") }}

## Resumen del curso

*Describe aquí los objetivos y contenido general del curso...*

## Sesiones

```dataview
TABLE semana as "Semana", sesion as "Tipo", estado as "Estado", fecha as "Fecha"
FROM "01_Universidad"
WHERE tipo = "sesion" AND curso_nombre = this.curso_nombre
SORT semana ASC
```

## Resúmenes por semana

```dataview
LIST
FROM "01_Universidad"
WHERE tipo = "resumen" AND curso_nombre = this.curso_nombre
SORT semana ASC
```

## Tareas

```dataview
TASK
FROM "01_Universidad"
WHERE !completed AND curso_nombre = this.curso_nombre
SORT file.name ASC
```
