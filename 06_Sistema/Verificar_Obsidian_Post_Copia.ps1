$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$ProjectDir = Join-Path $PSScriptRoot "ObsidianAcademia"
$VenvPython = Join-Path $ProjectDir ".venv\\Scripts\\python.exe"
$ScriptPath = Join-Path $PSScriptRoot "scripts\\validate_obsidian_postcopy.py"

if (-not (Test-Path $ScriptPath)) {
    throw "No se encontro el script de validacion en $ScriptPath"
}

$PythonExe = if (Test-Path $VenvPython) { $VenvPython } else { "python" }

& $PythonExe $ScriptPath
if ($LASTEXITCODE -ne 0) {
    throw "La verificacion post-copia detecto fallos."
}
