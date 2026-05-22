---
tipo: manual
fecha: 2026-05-22
tags:
  - sistema
  - manual
  - linux
  - git
  - github
---

# Manual: Publicación de `ObsidianPersonal` en GitHub

Este manual documenta cómo se subió el vault local al repo:

- `https://github.com/mikehernandez-bit/ObsidianPersonal.git`

## 1) Objetivo

Publicar la carpeta del vault en GitHub con:

1. `README.md` útil.
2. Ignorados correctos para evitar archivos pesados/no portables.
3. Commit y push a `main`.

## 2) Preparación del repo local

Si la carpeta aún no es repo git:

```bash
cd /run/media/mike/Acer/Users/jhoan/Documents/Obsidian/Personal
git init -b main
```

## 3) `.gitignore` recomendado para este vault

Se definió para evitar:

- `node_modules`
- binarios locales grandes de tooling (`ffmpeg-bin`, `piper`)
- artefactos generados y cachés

Archivo usado:

- `.gitignore` en raíz del vault.

## 4) README

Se creó `README.md` en la raíz con:

- descripción del vault
- estructura de carpetas
- requisitos base
- comandos de validación
- enlaces a manuales

## 5) Configuración del remoto GitHub

```bash
git remote add origin https://github.com/mikehernandez-bit/ObsidianPersonal.git
```

Si ya existe:

```bash
git remote set-url origin https://github.com/mikehernandez-bit/ObsidianPersonal.git
```

Verificar:

```bash
git remote -v
```

## 6) Commit y push

```bash
git add .
git commit -m "Initial vault publish with Linux manuals and README"
git push -u origin main
```

## 7) Posibles errores y solución

### 7.1 `not a git repository`

No se ejecutó `git init` dentro de la carpeta correcta.

### 7.2 rechazo por archivos grandes (>100MB)

Agregar rutas a `.gitignore` y quitar del index:

```bash
git rm -r --cached <ruta>
git commit -m "Remove large files from git tracking"
git push
```

### 7.3 autenticación fallida en push

Iniciar sesión con GitHub CLI o token:

```bash
gh auth login
```

o usar URL remota con credenciales/token.

## 8) Recomendación de mantenimiento

Antes de cada push:

```bash
git status
git diff --name-only
```

y verificar que no entren binarios/caches no deseados.

