---
tipo: resumen
curso: {{ curso | default("") }}
curso_nombre: "{{ curso_nombre | default('') }}"
semana: {{ semana | default("") }}
sesion: {{ sesion | default("") }}
fecha: {{ fecha }}
fecha_generacion: {{ fecha_generacion | default(fecha) }}
fuente: "{{ fuente | default('') }}"
estado: completado
tags:
  - academia
  - resumen
{% if curso %}  - {{ curso }}{% endif %}
---

# Resumen{% if curso_nombre %}: {{ curso_nombre }}{% endif %}{% if semana %} — Semana {{ semana }}{% endif %}

---

{{ contenido }}
