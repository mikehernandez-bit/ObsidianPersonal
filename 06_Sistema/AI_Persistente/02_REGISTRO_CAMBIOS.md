# Registro de Solicitudes y Cambios

## 2026-05-22
- Solicitud: Configurar sistema de memoria persistente en Obsidian para Codex.
- Acción: Se creó carpeta `06_Sistema/AI_Persistente` con instrucciones, contexto maestro, plantillas y registros.
- Resultado: Sistema base operativo.
- Próximo paso: Empezar a registrar cada conversación nueva.

## 2026-05-22 (actualización)
- Solicitud: Dejar la persistencia al 100% con contexto real del proyecto.
- Acción: Se completó `01_CONTEXTO_MAESTRO.md` con perfil, objetivos, estado técnico, decisiones y pendientes globales.
- Acción: Se registró el estado operativo de Syncthing/Piper/Ollama y el estado de GitHub push pendiente por autenticación.
- Resultado: Memoria persistente operativa y utilizable al iniciar cualquier sesión nueva.
- Próximo paso: Autenticar GitHub (`gh auth login`) y ejecutar push final.

## 2026-05-22 (cierre técnico y persistencia final)
- Solicitud: Dejar persistencia completa con todo lo realizado, dudas finales y pendientes reales.
- Acción: Se consolidó en `01_CONTEXTO_MAESTRO.md` el estado técnico completo (Syncthing, estructura de semanas/material, plantillas de sesión, backend IA, manuales y Git).
- Acción: Se documentó explícitamente la incidencia crítica de PDF en Obsidian (`0 de 0`) y todas las mitigaciones aplicadas.
- Acción: Se registraron pendientes finales accionables (reinicio+retest, prueba AppImage oficial, cierre GitHub push, validación final backend).
- Resultado: Persistencia actualizada al estado real del proyecto y lista para retomar sin pérdida de contexto.
- Próximo paso: Validar PDF tras reinicio; si falla, ejecutar prueba con Obsidian AppImage oficial.

## 2026-05-22 (contexto + solucion real PDF)
- Solicitud: Tener contexto del proyecto en IA persistencia y aclarar de que trata la solucion real de la incidencia PDF.
- Acción: Se actualizó `01_CONTEXTO_MAESTRO.md` con hipótesis técnica consolidada de regresión de renderer/paquete y solución operativa.
- Acción: Se documentó explícitamente la alternativa real de resolución: AppImage oficial de Obsidian o rollback de `electron39` a versión estable.
- Acción: Se creó registro detallado en `registros/2026-05-22_contexto-solucion-pdf-electron39.md`.
- Resultado: Persistencia alineada con el estado real y con criterio técnico claro para resolver `0 de 0`.
- Próximo paso: Ejecutar AppImage o rollback, validar `01_Universidad/PDF_TEST_OBSIDIAN.pdf`, y cerrar pendiente si renderiza.

## 2026-05-22 (cierre pruebas AppImage + decision operativa PDF externo)
- Solicitud: Probar solución AppImage y dejar política final de apertura de PDF.
- Acción: Se ejecutaron pruebas con AppImage `1.12.7` y `1.11.5`, incluyendo arranque con `--ozone-platform=x11` y `--disable-gpu`.
- Acción: Se validó que el PDF de prueba sigue en `0 de 0` dentro de Obsidian.
- Acción: Se actualizó `01_CONTEXTO_MAESTRO.md` con diagnóstico consolidado (incompatibilidad de renderer en entorno Linux actual) y decisión operativa.
- Resultado: Queda definido como estándar operativo abrir PDF en aplicación externa del sistema.
- Próximo paso: Mantener operación con app externa y reintentar visor interno solo tras cambios relevantes de entorno/driver/Obsidian.
