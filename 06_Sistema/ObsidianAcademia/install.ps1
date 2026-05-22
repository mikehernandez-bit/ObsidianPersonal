$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$ProjectDir = $PSScriptRoot
$VaultDir = (Resolve-Path (Join-Path $ProjectDir "..\\..")).Path
$ToolsDir = Join-Path $ProjectDir "tools"
$FfmpegBinDir = Join-Path $ToolsDir "ffmpeg-bin"
$PiperDir = Join-Path $ToolsDir "piper"
$VoicesDir = Join-Path $ToolsDir "voices"
$LogsDir = Join-Path $ProjectDir "logs"
$VenvDir = Join-Path $ProjectDir ".venv"
$ConfigPath = Join-Path $ProjectDir "config.yaml"

$FfmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$PiperUrl = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
$VoiceModelUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_10246/low/es_ES-mls_10246-low.onnx"
$VoiceConfigUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_10246/low/es_ES-mls_10246-low.onnx.json"
$OllamaModel = "gemma4:e4b"

function Write-Step($message) {
    Write-Host ""
    Write-Host $message -ForegroundColor Cyan
}

function Ensure-Directory($path) {
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}

function Download-File($url, $destination) {
    Invoke-WebRequest -Uri $url -OutFile $destination -UseBasicParsing
}

function Expand-ZipToTemp($zipPath, $tempDir) {
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
    Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
}

function Ensure-ConfigPaths {
    if (-not (Test-Path $ConfigPath)) {
        throw "No se encontro config.yaml en $ConfigPath"
    }

    $content = Get-Content -Path $ConfigPath -Raw
    $content = $content -replace 'path: ".*"', 'path: "..\\.."'
    $content = $content -replace 'exe: "tools\\\\ffmpeg-bin\\\\ffmpeg\.exe"', 'exe: "tools\\ffmpeg-bin\\ffmpeg.exe"'
    $content = $content -replace 'ffprobe: "tools\\\\ffmpeg-bin\\\\ffprobe\.exe"', 'ffprobe: "tools\\ffmpeg-bin\\ffprobe.exe"'
    $content = $content -replace 'exe: "tools\\\\piper\\\\piper\.exe"', 'exe: "tools\\piper\\piper.exe"'
    $content = $content -replace 'model: "tools\\\\voices\\\\es_ES-mls_10246-low\.onnx"', 'model: "tools\\voices\\es_ES-mls_10246-low.onnx"'
    $content = $content -replace 'config: "tools\\\\voices\\\\es_ES-mls_10246-low\.onnx\.json"', 'config: "tools\\voices\\es_ES-mls_10246-low.onnx.json"'
    Set-Content -Path $ConfigPath -Value $content -Encoding UTF8
}

function Install-Ffmpeg {
    Write-Step "[1/6] FFmpeg"
    Ensure-Directory $FfmpegBinDir

    if ((Test-Path (Join-Path $FfmpegBinDir "ffmpeg.exe")) -and (Test-Path (Join-Path $FfmpegBinDir "ffprobe.exe"))) {
        Write-Host "FFmpeg ya existe en $FfmpegBinDir" -ForegroundColor Green
        return
    }

    $zipPath = Join-Path $env:TEMP "obsidianacademia_ffmpeg.zip"
    $extractDir = Join-Path $env:TEMP "obsidianacademia_ffmpeg_extract"

    Download-File $FfmpegUrl $zipPath
    Expand-ZipToTemp $zipPath $extractDir

    $binFolder = Get-ChildItem -Path $extractDir -Recurse -Directory -Filter "bin" | Select-Object -First 1
    if (-not $binFolder) {
        throw "No se encontro la carpeta bin de FFmpeg en el zip descargado."
    }

    Copy-Item -Path (Join-Path $binFolder.FullName "*") -Destination $FfmpegBinDir -Recurse -Force
    Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
    Remove-Item $extractDir -Recurse -Force -ErrorAction SilentlyContinue

    Write-Host "FFmpeg instalado en $FfmpegBinDir" -ForegroundColor Green
}

function Install-Piper {
    Write-Step "[2/6] Piper y voz"
    Ensure-Directory $PiperDir
    Ensure-Directory $VoicesDir

    if (-not (Test-Path (Join-Path $PiperDir "piper.exe"))) {
        $zipPath = Join-Path $env:TEMP "obsidianacademia_piper.zip"
        $extractDir = Join-Path $env:TEMP "obsidianacademia_piper_extract"

        Download-File $PiperUrl $zipPath
        Expand-ZipToTemp $zipPath $extractDir
        Copy-Item -Path (Join-Path $extractDir "*") -Destination $PiperDir -Recurse -Force
        Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
        Remove-Item $extractDir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Piper instalado en $PiperDir" -ForegroundColor Green
    } else {
        Write-Host "Piper ya existe en $PiperDir" -ForegroundColor Green
    }

    $modelPath = Join-Path $VoicesDir "es_ES-mls_10246-low.onnx"
    $configPath = Join-Path $VoicesDir "es_ES-mls_10246-low.onnx.json"

    if (-not (Test-Path $modelPath)) {
        Download-File $VoiceModelUrl $modelPath
    }
    if (-not (Test-Path $configPath)) {
        Download-File $VoiceConfigUrl $configPath
    }

    Write-Host "Voz instalada en $VoicesDir" -ForegroundColor Green
}

function Install-PythonEnv {
    Write-Step "[3/6] Entorno Python"
    Ensure-Directory $LogsDir

    if (-not (Test-Path (Join-Path $VenvDir "Scripts\\python.exe"))) {
        python -m venv $VenvDir
    }

    $pythonExe = Join-Path $VenvDir "Scripts\\python.exe"
    & $pythonExe -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "Fallo la actualizacion de pip." }
    & $pythonExe -m pip install -r (Join-Path $ProjectDir "requirements.txt")
    if ($LASTEXITCODE -ne 0) { throw "Fallo la instalacion de dependencias Python." }

    Write-Host "Entorno virtual listo en $VenvDir" -ForegroundColor Green
}

function Ensure-OllamaModel {
    Write-Step "[4/6] Ollama"
    $ollama = Get-Command ollama -ErrorAction SilentlyContinue

    if (-not $ollama) {
        Write-Host "Ollama no esta instalado. Instala Ollama y luego ejecuta: ollama pull $OllamaModel" -ForegroundColor Yellow
        return
    }

    try {
        ollama pull $OllamaModel
        if ($LASTEXITCODE -ne 0) {
            throw "ollama pull devolvio un codigo distinto de cero."
        }
        Write-Host "Modelo $OllamaModel listo" -ForegroundColor Green
    } catch {
        Write-Host "No se pudo descargar $OllamaModel automaticamente. Ejecuta manualmente: ollama pull $OllamaModel" -ForegroundColor Yellow
    }
}

function Write-Prerequisites {
    Write-Step "[5/6] OCR opcional"
    Write-Host "Tesseract no se instala aqui. Es opcional: Gemma 4 Vision ya cubre imagenes y OCR queda como fallback." -ForegroundColor Yellow
}

function Validate-System {
    Write-Step "[6/6] Validacion"
    $pythonExe = Join-Path $VenvDir "Scripts\\python.exe"
    if (-not (Test-Path $pythonExe)) {
        throw "No se encontro el python del entorno virtual."
    }

    & $pythonExe (Join-Path $ProjectDir "main.py") validate
    if ($LASTEXITCODE -ne 0) {
        throw "La validacion del sistema local fallo."
    }
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " ObsidianAcademia local al vault" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Vault detectado: $VaultDir" -ForegroundColor DarkGray
Write-Host "Proyecto local: $ProjectDir" -ForegroundColor DarkGray

Ensure-ConfigPaths
Install-Ffmpeg
Install-Piper
Install-PythonEnv
Ensure-OllamaModel
Write-Prerequisites
Validate-System

Write-Host ""
Write-Host "Instalacion completada." -ForegroundColor Green
Write-Host "Usa este proyecto local desde el vault: $ProjectDir" -ForegroundColor Green
