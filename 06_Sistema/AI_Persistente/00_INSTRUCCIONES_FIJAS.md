# Instrucciones fijas para Codex (Persistencia)

## Objetivo
Mantener memoria operativa entre sesiones en este vault.

## Regla principal
En cada nueva conversación, pegar este bloque al inicio:

```txt
Usa como memoria persistente estos archivos:
- 06_Sistema/AI_Persistente/01_CONTEXTO_MAESTRO.md
- 06_Sistema/AI_Persistente/02_REGISTRO_CAMBIOS.md
- Último archivo en 06_Sistema/AI_Persistente/registros/

Antes de empezar:
1) Léelos.
2) Resume el estado actual en 5 bullets.
3) Ejecuta la solicitud.
4) Al finalizar, actualiza registro y pendientes.
```

## Convención de registro
- Toda solicitud nueva: agregar una entrada en `02_REGISTRO_CAMBIOS.md`.
- Todo cambio relevante: crear/actualizar nota en `registros/` con fecha.
- Formato de fecha: `YYYY-MM-DD`.

## Cierre de sesión
Siempre cerrar con:
- Qué se hizo
- Qué falta
- Próximo paso exacto
