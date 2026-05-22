---
tipo: programa_coursera
plataforma: coursera
programa: "{{ programa }}"
fecha_inicio: {{ fecha }}
estado: {{ estado | default("en_curso") }}
tags:
  - coursera
  - programa
---

# Programa: {{ programa }}

**Plataforma:** Coursera
**Fecha inicio:** {{ fecha }}
**Estado:** {{ estado | default("en_curso") }}

## Cursos del programa

```dataview
TABLE modulo as "Módulo", leccion as "Lección", estado as "Estado"
FROM "02_Coursera/Programa_{{ programa }}"
WHERE tipo = "leccion_coursera"
SORT file.name ASC
```

## Progreso

*Actualiza aquí tu avance...*
