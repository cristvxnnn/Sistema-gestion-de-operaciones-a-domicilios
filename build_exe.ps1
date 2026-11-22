$ErrorActionPreference = "Stop"

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCommand) {
    $pythonPath = $pythonCommand.Source
} else {
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        $pythonPath = $launcher.Source
    } else {
        $pythonPath = $null
    }
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

    $distDirectory = Join-Path $PSScriptRoot "dist"
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "instalar_domiya.ps1") `
        -Destination (Join-Path $distDirectory "instalar_domiya.ps1") -Force
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "README_INSTALACION.md") `
        -Destination (Join-Path $distDirectory "README_INSTALACION.md") -Force
    $sqlDirectory = Join-Path $distDirectory "database"
    New-Item -ItemType Directory -Path $sqlDirectory -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "database\SQL proyectoFinal.sql") `
        -Destination (Join-Path $sqlDirectory "SQL proyectoFinal.sql") -Force
} finally {
    Pop-Location
}

Write-Host "Ejecutable creado en: $(Join-Path $PSScriptRoot 'dist\DOMIYA.exe')"
