# Sesion 2026-05-22 - Contexto y solucion real incidencia PDF

## Solicitud
- Tener contexto del proyecto en IA persistencia y aclarar de que trata la solucion real:
  - usar Obsidian oficial AppImage, o
  - hacer rollback de `electron39` a version que si renderiza.

## Contexto del proyecto (resumen corto)
- Vault principal: `ObsidianPersonal`.
- Estado general: organizacion, sincronizacion y automatizaciones base operativas.
- Incidencia abierta: PDFs en Obsidian muestran `0 de 0` en Linux.
- Mitigaciones previas (cache, GPU off, plugins off, qpdf, copia a ruta Linux nativa) sin resolver el render.

## De que trata esta solucion
- No corrige contenido ni estructura del vault; corrige la capa de runtime/renderizado de la app.
- Objetivo: descartar o resolver una regresion del renderer PDF del paquete actual de Obsidian en Linux.
- Opcion A (preferida por simplicidad): usar la AppImage oficial de Obsidian con la misma bóveda.
- Opcion B: mantener paquete actual pero hacer rollback de `electron39` a una version estable que si renderiza PDF.

## Criterio tecnico de eleccion
- Si AppImage renderiza bien: confirma problema del paquete/runtime actual, y se puede operar con AppImage.
- Si rollback de `electron39` renderiza bien: confirma regresion especifica del runtime.
- En ambos casos, la solucion es de empaquetado/runtime, no de notas ni de Syncthing.

## Proximo paso exacto
- Abrir `01_Universidad/PDF_TEST_OBSIDIAN.pdf` con la opcion elegida.
- Si deja de aparecer `0 de 0`, marcar incidencia como resuelta y actualizar `01_CONTEXTO_MAESTRO.md`.
