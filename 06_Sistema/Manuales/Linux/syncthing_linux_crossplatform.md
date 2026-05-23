---
tipo: manual
fecha: 2026-05-22
tags:
  - sistema
  - manual
  - syncthing
  - linux
  - windows
  - android
  - ollama
  - piper
---

# Manual: Sync Linux + Windows + Android y ajustes cross-platform

Este manual documenta exactamente lo que se hizo en este proyecto para:

1. Habilitar Syncthing en Linux (CachyOS + Omarchy).
2. Integrarlo con los nodos existentes (Windows + celular).
3. Corregir comportamiento cross-platform del backend (`Windows`/`Linux`) en `ObsidianAcademia`.

Fecha de ejecución real: **2026-05-22**.

---

## 1) Contexto del problema

Escenario inicial:

- En Windows ya existía Syncthing con carpeta `Obsidian` compartida al celular.
- En Linux (dual boot del mismo equipo) **no estaba instalado/configurado Syncthing**.
- Resultado: cambios hechos desde Linux no se propagaban al celular hasta volver a Windows.

Además, en backend Python:

- `config.yaml` tenía rutas estilo Windows (`\`) y ejecutables `.exe`.
- En Linux, `ffmpeg.exe` y `piper.exe` no son ejecutables nativos.

---

## 2) Diagnóstico inicial ejecutado

Comandos de verificación:

```bash
which syncthing || true
systemctl --user is-enabled syncthing.service || true
systemctl --user is-active syncthing.service || true
ls -la ~/.config/syncthing || true
```

Resultado:

- `syncthing` no instalado.
- `syncthing.service` inexistente/inactivo.
- sin carpeta de configuración de Syncthing en Linux.

---

## 3) Instalación de Syncthing en Linux (modo usuario)

Nota: no se usó `pacman` por requerir `sudo` interactivo.
Se instaló binario local de usuario para no depender de root.

### 3.1 Descargar release oficial

```bash
curl -fsSL https://api.github.com/repos/syncthing/syncthing/releases/latest
curl -fL https://github.com/syncthing/syncthing/releases/download/v2.1.0/syncthing-linux-amd64-v2.1.0.tar.gz -o /tmp/syncthing-linux-amd64-v2.1.0.tar.gz
tar -xzf /tmp/syncthing-linux-amd64-v2.1.0.tar.gz -C /tmp
```

### 3.2 Instalar binario local

```bash
mkdir -p ~/.local/bin ~/.local/lib/syncthing
install -m 0755 /tmp/syncthing-linux-amd64-v2.1.0/syncthing ~/.local/bin/syncthing
~/.local/bin/syncthing --version
```

Versión instalada:

- `syncthing v2.1.0`

---

## 4) Servicio systemd --user para arranque automático

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
systemctl --user is-enabled syncthing.service
systemctl --user is-active syncthing.service
```

Estado final:

- `enabled`
- `active`

GUI local:

- `http://127.0.0.1:8384`

---

## 5) Integración de nodos (Linux + Windows + Celular)

### 5.1 IDs involucrados

- Linux (este nodo): `IKRPZXG-7AEW32Z-BZAB5PT-EKXBBZ7-QCEBEHT-O3P6BBL-HXVVZSE-HWB4WAZ`
- Celular: `IUNI7IH-VUUGC4O-R6NLNV6-BNOXXDF-UDVDZOT-P7OCIHR-XEQE4QO-U7GFPAH`
- Windows: `MMDO65C-7NRRE55-VL733EH-JLX6WPP-OKFBS2C-BNJPAKU-YQRKFTL-BG3RLAF`
- Folder ID Obsidian: `eugkg-2hgmr`

### 5.2 Config Linux (Syncthing local state)

Archivo editado:

- `~/.local/state/syncthing/config.xml`

Se añadió:

- Dispositivos `CelularXiaomi` y `MikeJhoan`.
- Carpeta `Obsidian` con:
  - `id="eugkg-2hgmr"`
  - `path="/run/media/mike/Acer/Users/jhoan/Documents/Obsidian/Personal"`
  - `type="sendreceive"`
  - asociada a los 3 devices (Linux, celular, Windows).

### 5.3 Config Windows (preparado desde Linux)

Archivo editado:

- `/run/media/mike/Acer/Users/jhoan/AppData/Local/Syncthing/config.xml`

Se añadió el device Linux `IKRPZXG...`:

- como `<device ... name="cachyos-x8664z">`
- y dentro del folder `eugkg-2hgmr`.

Esto deja listo el reconocimiento mutuo al iniciar Syncthing en Windows.

---

## 6) Verificación de estado

### 6.1 Servicio Linux

```bash
systemctl --user status syncthing.service --no-pager
journalctl --user -u syncthing.service -n 80 --no-pager
```

Se confirmó:

- listeners activos (`tcp/quic` en `22000`)
- GUI/API en `127.0.0.1:8384`
- carpeta `Obsidian` en estado `Ready to synchronize`

### 6.2 API local de Syncthing

Consultas usadas:

```bash
curl -fsS -H "X-API-Key: <API_KEY>" http://127.0.0.1:8384/rest/system/status
curl -fsS -H "X-API-Key: <API_KEY>" http://127.0.0.1:8384/rest/system/connections
curl -fsS -H "X-API-Key: <API_KEY>" "http://127.0.0.1:8384/rest/db/status?folder=eugkg-2hgmr"
```

Resultado de carpeta:

- `state: "idle"`
- `needFiles: 0`
- `needTotalItems: 0`

### 6.3 Paso de GUI que puede aparecer: "Compartir carpeta"

Si Syncthing muestra el diálogo **Compartir carpeta** para `Obsidian`:

1. Marcar dispositivos:
   - `CelularXiaomi`
   - `MikeJhoan` (Windows)
2. Confirmar en **Compartir**.
3. En Android, si aparece solicitud de carpeta entrante, **Aceptar**.

Esto termina de cerrar la malla de sincronización entre los 3 nodos.

---

## 7) Ajuste cross-platform en backend ObsidianAcademia

### 7.1 Problema detectado

`config.yaml` usa rutas como:

- `tools\ffmpeg-bin\ffmpeg.exe`
- `tools\piper\piper.exe`

En Linux:

- `ffmpeg.exe` puede existir pero no ejecuta (`Exec format error`).
- `piper.exe` también falla por ser binario Windows.

### 7.2 Cambios de código aplicados

Archivo:

- `06_Sistema/ObsidianAcademia/src/config/settings.py`

Cambios:

1. Normalización de rutas:
   - reemplazo `\` por `/` en `_resolve_path`.
2. Nuevo resolvedor de ejecutables con fallback:
   - `_resolve_executable(...)`.
3. Lógica en Linux:
   - si la ruta termina en `.exe`, prioriza binario nativo encontrado con `shutil.which(...)`.
4. Aplicado a:
   - `ffmpeg`, `ffprobe`, `piper`.

Archivo:

- `06_Sistema/ObsidianAcademia/src/utils/validators.py`

Cambio:

- `validate_piper(...)` ahora intenta ejecutar `piper --help` y falla explícitamente si no es ejecutable.
- Evita falso positivo de "archivo existe pero no corre".

---

## 8) Estado final real tras cambios

### Syncthing

- Linux: instalado, activo, autostart, carpeta compartida configurada.
- Windows config: preparada para incluir nodo Linux.
- Celular: aceptación manual del nuevo device Linux completada.
- Estado validado por API:
  - carpeta `eugkg-2hgmr` en `idle`
  - `needTotalItems: 0`
  - `errors: 0`
  - celular conectado (`connected: true`)
  - Windows puede aparecer desconectado cuando no está iniciado (esperado).

### Backend (Python)

- `ffmpeg` y `ffprobe` en Linux quedan resueltos a binarios nativos (`/usr/bin/...`).
- `piper.exe` sigue siendo Windows-only: para Linux se necesita `piper` nativo.
- Ollama sigue dependiendo de servicio local activo (`ollama serve`).

---

## 9) Checklist de replicación en otro proyecto

1. Instalar Syncthing en Linux (usuario o paquete del sistema).
2. Crear servicio `systemd --user`, habilitar y arrancar.
3. Abrir GUI en `127.0.0.1:8384`.
4. Configurar folder compartido con ruta Linux real.
5. Agregar devices de Windows y Android.
6. Verificar conexiones y estado (`need=0`, `idle`).
7. Si hay backend cross-platform:
   - normalizar rutas
   - fallback de ejecutables por SO
   - validar ejecución real, no solo existencia de archivo.

---

## 10) Archivos clave tocados en este proyecto

- `~/.config/systemd/user/syncthing.service`
- `~/.local/state/syncthing/config.xml`
- `/run/media/mike/Acer/Users/jhoan/AppData/Local/Syncthing/config.xml`
- `06_Sistema/ObsidianAcademia/src/config/settings.py`
- `06_Sistema/ObsidianAcademia/src/utils/validators.py`
