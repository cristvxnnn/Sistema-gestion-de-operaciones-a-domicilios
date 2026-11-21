$ErrorActionPreference = "Stop"

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCommand -and $pythonCommand.Source -notlike "*\Microsoft\WindowsApps\python.exe") {
    $pythonPath = $pythonCommand.Source
} else {
    $pythonPath = Join-Path $env:LOCALAPPDATA "Python\pythoncore-3.14-64\python.exe"
}
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "No encontré Python. Edita build_exe.ps1 para apuntar a tu python.exe."
}

Push-Location $PSScriptRoot
try {
    & $pythonPath -m PyInstaller --clean --noconfirm (Join-Path $PSScriptRoot "domiya.spec")
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller terminó con código $LASTEXITCODE."
    }

    $configLocal = Join-Path $PSScriptRoot "database\config_local.py"
    if (Test-Path -LiteralPath $configLocal) {
        $configDirectory = Join-Path $PSScriptRoot "dist\database"
        New-Item -ItemType Directory -Path $configDirectory -Force | Out-Null
        Copy-Item -LiteralPath $configLocal `
            -Destination (Join-Path $configDirectory "config_local.py") -Force
    }
} finally {
    Pop-Location
}

Write-Host "Ejecutable creado en: $(Join-Path $PSScriptRoot 'dist\DOMIYA.exe')"
