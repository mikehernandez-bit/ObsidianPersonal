---
tipo: semana
curso: {{ curso }}
curso_nombre: "{{ curso_nombre }}"
semana: {{ semana }}
estado: {{ estado | default("pendiente") }}
fecha: {{ fecha }}
tags:
  - academia
  - semana
  - {{ curso }}
---

# Semana {{ semana }} — {{ curso_nombre }}

## Teoría

```dataview
LIST
FROM "01_Universidad/Curso_{{ curso }}/Semana_{{ '%02d' | format(semana) }}/Teoria"
SORT file.name ASC
```

## Práctica

```dataview
LIST
FROM "01_Universidad/Curso_{{ curso }}/Semana_{{ '%02d' | format(semana) }}/Practica"
SORT file.name ASC
```

## Tareas de la semana

```dataview
TASK
FROM "01_Universidad/Curso_{{ curso }}/Semana_{{ '%02d' | format(semana) }}"
WHERE !completed
```

## Reflexión semanal

*¿Qué aprendí esta semana? ¿Qué me quedó pendiente?*
