---
tipo: cuestionario
curso: {{ curso | default("") }}
curso_nombre: "{{ curso_nombre | default('') }}"
semana: {{ semana | default("") }}
sesion: {{ sesion | default("") }}
fecha: {{ fecha }}
fecha_generacion: {{ fecha_generacion | default(fecha) }}
fuente: "{{ fuente | default('') }}"
estado: completado
intentos: 0
mejor_puntaje: ""
tags:
  - academia
  - cuestionario
  - estudio
{% if curso %}  - {{ curso }}{% endif %}
---

# Cuestionario{% if curso_nombre %}: {{ curso_nombre }}{% endif %}{% if semana %} — Semana {{ semana }}{% endif %}

> [!TIP] Instrucciones
> Intenta responder sin ver las respuestas. Luego compara con la sección de respuestas al final.

---

{{ contenido }}
