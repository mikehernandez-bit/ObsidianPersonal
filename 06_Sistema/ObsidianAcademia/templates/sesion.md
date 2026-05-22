---
id: {{ id }}
tipo: sesion
curso: {{ curso }}
curso_nombre: "{{ curso_nombre }}"
semana: {{ semana }}
sesion: {{ tipo }}
fecha: {{ fecha }}
estado: {{ estado | default("en_proceso") }}
transcript_status: {{ transcript_status | default("pendiente") }}
summary_status: {{ summary_status | default("pendiente") }}
quiz_status: {{ quiz_status | default("pendiente") }}
audio_status: {{ audio_status | default("pendiente") }}
tags:
  - academia
  - sesion
  - {{ curso }}
  - {{ tipo | lower }}
---

# {{ curso_nombre }} — Semana {{ semana }} — {{ tipo }}

**Fecha:** {{ fecha }}

## Productos generados

{{ contenido | default("*Pendiente de procesamiento...*") }}

## Notas de clase

*Escribe aquí tus notas durante la clase...*

## Preguntas durante la clase

- 

## Temas vistos

- 

## Tareas asignadas

- [ ] 
