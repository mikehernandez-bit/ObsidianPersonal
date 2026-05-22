---
tipo: modulo_coursera
plataforma: coursera
curso: "{{ curso }}"
modulo: "{{ modulo }}"
fecha: {{ fecha }}
estado: {{ estado | default("en_curso") }}
tags:
  - coursera
  - modulo
---

# Módulo: {{ modulo }}

**Curso:** {{ curso }}
**Estado:** {{ estado | default("en_curso") }}

## Lecciones

```dataview
LIST
FROM "02_Coursera"
WHERE tipo = "leccion_coursera" AND modulo = "{{ modulo }}" AND curso = "{{ curso }}"
SORT leccion ASC
```

## Objetivos del módulo

- 

## Notas del módulo

{{ contenido | default("*Escribe aquí tus notas...*") }}
