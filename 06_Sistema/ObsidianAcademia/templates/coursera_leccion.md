---
tipo: leccion_coursera
plataforma: coursera
programa: "{{ programa | default('') }}"
curso: "{{ curso }}"
modulo: "{{ modulo }}"
leccion: "{{ leccion }}"
fecha: {{ fecha }}
estado: {{ estado | default("completado") }}
tags:
  - coursera
  - leccion
---

# {{ leccion }}

**Curso:** {{ curso }}
**Módulo:** {{ modulo }}
{% if programa %}**Programa:** {{ programa }}{% endif %}
**Fecha:** {{ fecha }}

## Productos

{{ contenido | default("*Pendiente de procesamiento...*") }}

## Notas de la lección

*Escribe aquí tus notas...*

## Puntos clave

- 

## Dudas

- 
