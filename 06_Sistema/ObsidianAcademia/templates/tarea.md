---
tipo: tarea
curso: {{ curso }}
curso_nombre: "{{ curso_nombre }}"
semana: {{ semana | default("") }}
titulo: "{{ titulo }}"
fecha_asignacion: {{ fecha }}
fecha_entrega: {{ fecha_entrega | default("") }}
estado: {{ estado | default("pendiente") }}
calificacion: {{ calificacion | default("") }}
tags:
  - academia
  - tarea
  - {{ curso }}
---

# Tarea: {{ titulo }}

**Curso:** {{ curso_nombre }}
**Fecha asignada:** {{ fecha }}
**Fecha de entrega:** {{ fecha_entrega | default("*Por definir*") }}
**Estado:** {{ estado | default("pendiente") }}

## Descripción

{{ contenido | default("*Describe la tarea aquí...*") }}

## Requisitos

- [ ] 

## Desarrollo

*Escribe tu desarrollo aquí...*

## Archivos adjuntos

- 

## Notas

- 
