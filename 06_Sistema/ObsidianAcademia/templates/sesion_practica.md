---
tipo: sesion_practica
curso: {{ curso }}
curso_nombre: "{{ curso_nombre }}"
semana: {{ semana }}
sesion: Practica
fecha: {{ fecha }}
estado: {{ estado | default("en_proceso") }}
tags:
  - academia
  - practica
  - {{ curso }}
---

# Práctica — {{ curso_nombre }} — Semana {{ semana }}

**Fecha:** {{ fecha }}
**Profesor:** {{ profesor | default("") }}
**Tema:** {{ tema | default("") }}

## Objetivos de la práctica

- 

## Ejercicios resueltos

### Ejercicio 1

**Enunciado:**

**Solución:**

### Ejercicio 2

**Enunciado:**

**Solución:**

## Herramientas utilizadas

- 

## Código / Procedimiento

```
(Código o procedimiento aquí)
```

## Resultados

{{ contenido | default("*Pendiente...*") }}

## Observaciones

- 

## Tareas de práctica

- [ ] 
