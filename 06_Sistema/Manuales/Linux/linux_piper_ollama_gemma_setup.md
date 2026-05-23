---
tipo: manual
fecha: 2026-05-22
tags:
  - sistema
  - manual
  - linux
  - cachyos
  - omarchy
  - syncthing
  - piper
  - ollama
  - gemma
---

# Manual Linux: Syncthing + Piper + Ollama + Gemma

Manual técnico completo de lo que se hizo en Linux para que:

1. El vault de Obsidian sincronice entre Linux + Windows + celular.
2. El backend `ObsidianAcademia` funcione en Linux.
3. Quede documentado por qué algunos binarios van fuera del vault.

Entorno real usado:

- SO: CachyOS + Omarchy
- Vault: `/run/media/mike/Acer/Users/jhoan/Documents/Obsidian/Personal`
- Fecha de implementación: 2026-05-22

---

## 1) Problema inicial detectado

### 1.1 Sincronización

- Windows ya tenía Syncthing configurado.
- Linux no tenía Syncthing instalado/configurado.
- Celular no veía cambios hechos desde Linux hasta reiniciar en Windows.

### 1.2 Backend IA

En `06_Sistema/ObsidianAcademia/config.yaml` había rutas estilo Windows:

- `tools\\ffmpeg-bin\\ffmpeg.exe`
- `tools\\piper\\piper.exe`
- `logs\\academia.log`

Impacto en Linux:

- `.exe` de Windows no ejecuta en Linux.
- ruta con `\` puede crear nombre de archivo inválido para Android (`logs\academia.log` literal).

---

## 2) Syncthing en Linux (paso a paso)

## 2.1 Diagnóstico

Se verificó que no existía Syncthing:

```bash
which syncthing
systemctl --user is-enabled syncthing.service
systemctl --user is-active syncthing.service
```

Resultado: no instalado.

## 2.2 Instalación en usuario (sin meter binarios al vault)

Se descargó release oficial y se instaló en `~/.local/bin`:

```bash
mkdir -p ~/.local/bin ~/.local/lib/syncthing
curl -fL https://github.com/syncthing/syncthing/releases/download/v2.1.0/syncthing-linux-amd64-v2.1.0.tar.gz -o /tmp/syncthing-linux-amd64-v2.1.0.tar.gz
tar -xzf /tmp/syncthing-linux-amd64-v2.1.0.tar.gz -C /tmp
install -m 0755 /tmp/syncthing-linux-amd64-v2.1.0/syncthing ~/.local/bin/syncthing
~/.local/bin/syncthing --version
```

## 2.3 Servicio systemd de usuario

Archivo creado:

- `~/.config/systemd/user/syncthing.service`

Contenido:

```ini
[Unit]
Description=Syncthing - Open Source Continuous File Synchronization
Documentation=man:syncthing(1)
After=network.target

[Service]
ExecStart=/home/mike/.local/bin/syncthing serve --no-browser --no-restart --logflags=0
Restart=on-failure
RestartSec=5
SuccessExitStatus=3 4

[Install]
WantedBy=default.target
```

Activación:

```bash
systemctl --user daemon-reload
systemctl --user enable --now syncthing.service
systemctl --user is-active syncthing.service
```

GUI:

- `http://127.0.0.1:8384`

## 2.4 Integración de dispositivos y carpeta

IDs usados:

- Linux: `IKRPZXG-7AEW32Z-BZAB5PT-EKXBBZ7-QCEBEHT-O3P6BBL-HXVVZSE-HWB4WAZ`
- Celular: `IUNI7IH-VUUGC4O-R6NLNV6-BNOXXDF-UDVDZOT-P7OCIHR-XEQE4QO-U7GFPAH`
- Windows: `MMDO65C-7NRRE55-VL733EH-JLX6WPP-OKFBS2C-BNJPAKU-YQRKFTL-BG3RLAF`
- Folder ID Obsidian: `eugkg-2hgmr`

Ruta Linux de carpeta compartida:

- `/run/media/mike/Acer/Users/jhoan/Documents/Obsidian/Personal`

Se editó:

- `~/.local/state/syncthing/config.xml`
- `/run/media/mike/Acer/Users/jhoan/AppData/Local/Syncthing/config.xml`

para incluir Linux en el set de devices de `Obsidian`.

## 2.5 Error real encontrado y corregido

Elemento no sincronizado:

- `06_Sistema/ObsidianAcademia/logs\academia.log`

Causa:

- ruta de log en formato Windows dentro de Linux.

Corrección:

1. En `config.yaml`, cambiar:
   - `logging.file: "logs\\academia.log"` → `logging.file: "logs/academia.log"`
2. Mover archivo:
   - `logs\academia.log` → `logs/academia.log`
3. Reescanear Syncthing.

---

## 3) Ajustes cross-platform en código del backend

Archivo:

- `06_Sistema/ObsidianAcademia/src/config/settings.py`

Cambios aplicados:

1. Normalización de separadores:
   - `raw_path.replace("\\", "/")`.
2. Nueva resolución de ejecutables con fallback:
   - `_resolve_executable(...)`.
3. Regla Linux:
   - si ruta termina en `.exe`, prioriza binario nativo (`shutil.which`).
4. Aplicado a:
   - `ffmpeg`
   - `ffprobe`
   - `piper`

Archivo:

- `06_Sistema/ObsidianAcademia/src/utils/validators.py`

Cambio:

- `validate_piper(...)` ahora prueba ejecución real (`piper --help`) y falla si no es ejecutable.

Resultado:

- validación detecta errores reales en Linux y evita falsos positivos.

---

## 4) Piper en Linux: qué se hizo y por qué

## 4.1 Objetivo

Evitar `piper.exe` (Windows-only) y usar `piper` nativo Linux.

## 4.2 Instalación realizada

Como `python3 -m pip` no estaba disponible globalmente, se creó venv local:

```bash
python3 -m venv ~/.local/lib/piper-venv
~/.local/lib/piper-venv/bin/pip install -U pip piper-tts
ln -sf ~/.local/lib/piper-venv/bin/piper ~/.local/bin/piper
~/.local/bin/piper --help
```

Resultado:

- `piper` disponible en `/home/mike/.local/bin/piper`.
- backend ya lo detecta y valida.

## 4.3 Modelo de voz

Se reutilizó el modelo ya existente en el vault:

- `06_Sistema/ObsidianAcademia/tools/voices/es_ES-mls_10246-low.onnx`
- `06_Sistema/ObsidianAcademia/tools/voices/es_ES-mls_10246-low.onnx.json`

No fue necesario descargarlo de nuevo.

---

## 5) Ollama en Linux: instalación y servicio

## 5.1 Instalación binaria

```bash
curl -fL https://github.com/ollama/ollama/releases/download/v0.24.0/ollama-linux-amd64.tar.zst -o /tmp/ollama-linux-amd64.tar.zst
mkdir -p ~/.local/lib/ollama
tar --zstd -xf /tmp/ollama-linux-amd64.tar.zst -C ~/.local/lib/ollama
install -m 0755 ~/.local/lib/ollama/bin/ollama ~/.local/bin/ollama
```

## 5.2 Servicio de usuario

Archivo:

- `~/.config/systemd/user/ollama.service`

Contenido:

```ini
[Unit]
Description=Ollama Service
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/home/mike/.local/bin/ollama serve
Restart=on-failure
RestartSec=5
Environment=OLLAMA_HOST=127.0.0.1:11434

[Install]
WantedBy=default.target
```

Activación:

```bash
systemctl --user daemon-reload
systemctl --user enable --now ollama.service
systemctl --user is-active ollama.service
```

Endpoint esperado:

- `http://127.0.0.1:11434`

---

## 6) Descarga de modelo Gemma (`gemma4:e4b`)

Modelo configurado en proyecto:

- `gemma4:e4b`

Comando:

```bash
~/.local/bin/ollama pull gemma4:e4b
```

Notas reales:

- descarga grande (~9.6 GB), tarda bastante.
- para no bloquear sesión interactiva, se puede lanzar como unidad transient:

```bash
systemd-run --user --unit ollama-pull-gemma4 --collect /home/mike/.local/bin/ollama pull gemma4:e4b
```

Verificación:

```bash
systemctl --user status ollama-pull-gemma4.service
~/.local/bin/ollama list
```

Estado final logrado:

- `ollama list` muestra `gemma4:e4b`.

---

## 7) Por qué no instalar Piper/Ollama dentro del vault

No se colocaron binarios en `Obsidian/Personal` por diseño, no por omisión.

Razones:

1. Cross-platform limpio:
   - Linux, Windows y Android no comparten ejecutables compatibles.
2. Syncthing:
   - evitar sincronizar binarios gigantes o incompatibles entre nodos.
3. Mantenibilidad:
   - runtime del sistema en `~/.local/*`
   - contenido del proyecto en el vault.
4. Menos conflictos:
   - se evitan “no sincronizados” por archivos de SO.

Patrón recomendado:

- **Dentro del vault**: notas, scripts del proyecto, modelos reutilizables, config del proyecto.
- **Fuera del vault**: ejecutables del runtime (`syncthing`, `piper`, `ollama`), servicios `systemd`, caches.

---

## 8) Validación final del backend

Comando:

```bash
/tmp/oa-venv/bin/python 06_Sistema/ObsidianAcademia/main.py validate
```

Interpretación:

- `FFmpeg` OK
- `Piper` OK
- `Ollama` OK solo cuando `ollama serve` está activo y `gemma4:e4b` está en `ollama list`

---

## 9) Checklist rápido de replicación

1. Instalar Syncthing en `~/.local/bin` y servicio `--user`.
2. Configurar carpeta del vault con ruta Linux y devices remotos.
3. Corregir rutas con `\` a `/` en config de backend.
4. Instalar `piper` Linux (`piper-tts`) en venv local y enlazar en `~/.local/bin`.
5. Instalar `ollama` Linux en `~/.local/bin`.
6. Crear/activar `ollama.service` de usuario.
7. Descargar `gemma4:e4b`.
8. Ejecutar `main.py validate`.
9. Verificar Syncthing `idle` y `need=0`.

---

## 10) Archivos clave de esta implementación

Sistema Linux:

- `~/.config/systemd/user/syncthing.service`
- `~/.config/systemd/user/ollama.service`
- `~/.local/state/syncthing/config.xml`

Proyecto:

- `06_Sistema/ObsidianAcademia/config.yaml`
- `06_Sistema/ObsidianAcademia/src/config/settings.py`
- `06_Sistema/ObsidianAcademia/src/utils/validators.py`
- `06_Sistema/ObsidianAcademia/logs/academia.log`

Windows (preparación de malla Syncthing):

- `/run/media/mike/Acer/Users/jhoan/AppData/Local/Syncthing/config.xml`

