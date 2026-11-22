$ErrorActionPreference = "Stop"

$pythonPath = $null
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

if (-not $pythonPath) {
    $carpetasPython = @()
    $localAppData = [Environment]::GetFolderPath("LocalApplicationData")
    if ($localAppData) {
        $carpetasPython += Join-Path $localAppData "Python\pythoncore-3.14-64\python.exe"
    }
    if ($env:USERPROFILE) {
        $carpetasPython += Join-Path $env:USERPROFILE "AppData\Local\Python\pythoncore-3.14-64\python.exe"
    }
    $pythonPath = $carpetasPython | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}

if (-not $pythonPath) {
    throw "No encontré Python 3. Edita build_exe.ps1 para apuntar a tu python.exe."
}

Push-Location $PSScriptRoot
try {
    $specPath = Join-Path $PSScriptRoot "domiya.spec"
    & $pythonPath -m PyInstaller --clean --noconfirm $specPath
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller terminó con código $LASTEXITCODE."
    }

    $carpetaDistribucion = Join-Path $PSScriptRoot "dist\EntreCali"
    $carpetaConfig = Join-Path $carpetaDistribucion "database"
    New-Item -ItemType Directory -Path $carpetaConfig -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "database\config_local.example.py") `
        -Destination (Join-Path $carpetaConfig "config_local.py") -Force
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "GUIA_INSTALACION.md") `
        -Destination (Join-Path $carpetaDistribucion "LEEME_INSTALACION.md") -Force

    # Remove a prior one-file build so recipients only see the current distribution.
    $ejecutableAnterior = Join-Path $PSScriptRoot "dist\EntreCali.exe"
    if (Test-Path -LiteralPath $ejecutableAnterior) {
        Remove-Item -LiteralPath $ejecutableAnterior -Force
    }

    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "instalar_domiya.ps1") `
        -Destination (Join-Path $carpetaDistribucion "instalar_domiya.ps1") -Force
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "README_INSTALACION.md") `
        -Destination (Join-Path $carpetaDistribucion "README_INSTALACION.md") -Force
    $sqlDirectory = Join-Path $carpetaDistribucion "database"
    New-Item -ItemType Directory -Path $sqlDirectory -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "database\SQL proyectoFinal.sql") `
        -Destination (Join-Path $sqlDirectory "SQL proyectoFinal.sql") -Force
    $archivoZip = Join-Path $PSScriptRoot "dist\EntreCali.zip"
    if (Test-Path -LiteralPath $archivoZip) {
        Remove-Item -LiteralPath $archivoZip -Force
    }
    Compress-Archive -LiteralPath $carpetaDistribucion -DestinationPath $archivoZip -CompressionLevel Optimal
} finally {
    Pop-Location
}

Write-Host "Carpeta lista: $(Join-Path $PSScriptRoot 'dist\EntreCali')"
Write-Host "Archivo para compartir: $(Join-Path $PSScriptRoot 'dist\EntreCali.zip')"
