# Sesion 2026-05-22 - Cierre pruebas AppImage y politica PDF externo

## Solicitud
- Probar y cerrar la incidencia de visualizacion PDF en Obsidian.
- Si no se resuelve, dejar politica operativa clara en AI_Persistente.

## Pruebas ejecutadas
- AppImage oficial `1.12.7` (extraida por falta de FUSE en sistema): sin resolver `0 de 0`.
- AppImage oficial `1.11.5` (extraida): sin resolver `0 de 0`.
- AppImage `1.11.5` con `--ozone-platform=x11 --disable-gpu`: sin resolver `0 de 0`.

## Resultado tecnico
- La falla no queda acotada a una sola version (`1.12.x`) ni solo a `electron39`.
- Estado consolidado: incompatibilidad del renderer PDF de Obsidian con el entorno grafico Linux actual.

## Decision operativa
- Politica vigente: PDF siempre en aplicacion externa del sistema.
- El flujo de notas y sincronizacion continua normal; solo cambia el visor PDF.

## Proximo paso exacto
- Mantener apertura externa como estandar.
- Reintentar visor interno solo tras cambios relevantes de entorno (drivers/sesion grafica/actualizacion mayor de Obsidian).
