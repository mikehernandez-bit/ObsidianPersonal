---
tipo: curso_coursera
plataforma: coursera
programa: "{{ programa | default('') }}"
curso: "{{ curso }}"
fecha_inicio: {{ fecha }}
estado: {{ estado | default("en_curso") }}
tags:
  - coursera
  - curso
---

# Curso: {{ curso }}

**Plataforma:** Coursera
{% if programa %}**Programa:** {{ programa }}{% endif %}
**Fecha inicio:** {{ fecha }}
**Estado:** {{ estado | default("en_curso") }}

## Módulos

```dataview
TABLE leccion as "Lección", estado as "Estado"
FROM "02_Coursera"
WHERE tipo = "leccion_coursera" AND curso = "{{ curso }}"
SORT modulo ASC, leccion ASC
```

## Notas generales

*Resumen de lo aprendido en este curso...*
