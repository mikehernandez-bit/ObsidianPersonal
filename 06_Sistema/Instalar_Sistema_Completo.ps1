$ErrorActionPreference = "Stop"

$ProjectDir = Join-Path $PSScriptRoot "ObsidianAcademia"
$InstallScript = Join-Path $ProjectDir "install.ps1"
$PostCopyValidation = Join-Path $PSScriptRoot "Verificar_Obsidian_Post_Copia.ps1"

if (-not (Test-Path $InstallScript)) {
    throw "No se encontro el instalador local en $InstallScript"
}

& $InstallScript

if (Test-Path $PostCopyValidation) {
    & $PostCopyValidation
}
