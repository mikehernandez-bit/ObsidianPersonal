---
tipo: transcript
fuente: "{{ fuente | default('') }}"
idioma: {{ idioma | default("es") }}
duracion: "{{ duracion | default('') }}"
segmentos: {{ segmentos | default("0") }}
fecha: {{ fecha }}
curso: {{ curso | default("") }}
semana: {{ semana | default("") }}
sesion: {{ sesion | default("") }}
estado: completado
tags:
  - academia
  - transcript
{% if curso %}  - {{ curso }}{% endif %}
---

# Transcripción: {{ fuente | default("audio") }}

- **Idioma:** {{ idioma | default("español") }}
- **Duración:** {{ duracion | default("desconocida") }}
- **Segmentos:** {{ segmentos | default("N/A") }}

---

{{ contenido }}
