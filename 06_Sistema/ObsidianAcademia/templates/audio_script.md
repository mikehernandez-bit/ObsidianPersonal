---
tipo: audio_script
curso: {{ curso | default("") }}
curso_nombre: "{{ curso_nombre | default('') }}"
semana: {{ semana | default("") }}
sesion: {{ sesion | default("") }}
fecha: {{ fecha }}
fecha_generacion: {{ fecha_generacion | default(fecha) }}
fuente: "{{ fuente | default('') }}"
audio_generado: {{ audio_generado | default("false") }}
estado: completado
tags:
  - academia
  - audio_script
{% if curso %}  - {{ curso }}{% endif %}
---

# Guion de audio explicativo{% if curso_nombre %}: {{ curso_nombre }}{% endif %}{% if semana %} — Semana {{ semana }}{% endif %}

> [!NOTE] Este guion fue generado para ser convertido a audio con Piper TTS.
> Si el audio ya fue generado, lo encontrarás como `audio_explicativo.wav` en la misma carpeta.

---

{{ contenido }}
