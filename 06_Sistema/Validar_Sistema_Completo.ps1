$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$ProjectDir = Join-Path $PSScriptRoot "ObsidianAcademia"
$PythonExe = Join-Path $ProjectDir ".venv\\Scripts\\python.exe"
$MainPy = Join-Path $ProjectDir "main.py"

if (-not (Test-Path $PythonExe)) {
    throw "No se encontro .venv. Ejecuta primero 06_Sistema\\Instalar_Sistema_Completo.ps1"
}

& $PythonExe $MainPy validate
if ($LASTEXITCODE -ne 0) {
    throw "La validacion local devolvio error."
}
