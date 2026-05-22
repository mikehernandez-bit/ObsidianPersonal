---
tipo: informe
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
  - informe
{% if curso %}  - {{ curso }}{% endif %}
---

# Informe de sesión

**Curso:** {{ curso_nombre | default(curso) }}
**Semana:** {{ semana }}
**Tipo:** {{ sesion }}
**Fecha:** {{ fecha }}

---

{{ contenido }}
