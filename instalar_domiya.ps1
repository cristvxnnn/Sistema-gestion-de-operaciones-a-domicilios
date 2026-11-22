[CmdletBinding()]
param(
    [string]$DbHost = "127.0.0.1",
    [int]$DbPort = 3306,
    [string]$DbUser = "root",
    [string]$DbPassword = "root",
    [string]$DbName = "proyectofinal",
    [switch]$SkipDatabase
)

$ErrorActionPreference = "Stop"
$AppRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$SqlFile = Join-Path $AppRoot "database\SQL proyectoFinal.sql"

if ($DbName -ne "proyectofinal") {
    throw "El archivo SQL demo está preparado para la base de datos 'proyectofinal'."
}

function Find-MySqlClient {
    $command = Get-Command mysql -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $command = Get-Command mariadb -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $candidates = @(
        "$env:ProgramFiles\MariaDB 11.4\bin\mariadb.exe",
        "$env:ProgramFiles\MariaDB 11.3\bin\mariadb.exe",
        "$env:ProgramFiles\MariaDB 11.2\bin\mariadb.exe",
        "$env:ProgramFiles\MariaDB 11.1\bin\mariadb.exe",
        "$env:ProgramFiles\MariaDB 11.0\bin\mariadb.exe",
        "$env:ProgramFiles\MySQL\MySQL Server 8.0\bin\mysql.exe",
        "$env:ProgramFiles\MySQL\MySQL Server 8.4\bin\mysql.exe"
    )
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }
    return $null
}

function Start-DatabaseService {
    $services = Get-Service -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -match "^(MariaDB|mysql|MySQL.*)$"
        }
    foreach ($service in $services) {
        if ($service.Status -ne "Running") {
            Start-Service -Name $service.Name
        }
        return
    }
}

function Install-MariaDb {
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw "No se encontró MariaDB/MySQL ni winget. Instala MariaDB manualmente y vuelve a ejecutar este archivo."
    }

    Write-Host "No se encontró MariaDB/MySQL. Intentando instalar MariaDB con winget..."
    & $winget.Source install --id MariaDB.Server --exact --silent `
        --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        throw "winget no pudo instalar MariaDB. Instálalo manualmente y vuelve a ejecutar este archivo."
    }
}

function Wait-ForDatabase {
    param([string]$HostName, [int]$Port)
    for ($attempt = 1; $attempt -le 30; $attempt++) {
        if (Test-NetConnection -ComputerName $HostName -Port $Port `
                -InformationLevel Quiet -WarningAction SilentlyContinue) {
            return
        }
        Start-Sleep -Seconds 1
    }
    throw "El servidor de base de datos no respondió en ${HostName}:${Port}."
}

function Invoke-MySqlQuery {
    param([string]$Client, [string]$Query)
    $output = & $Client "--host=$DbHost" "--port=$DbPort" "--user=$DbUser" `
        "--password=$DbPassword" "--batch" "--skip-column-names" `
        "--default-character-set=utf8mb4" "--execute=$Query" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw ($output -join "`n")
    }
    return ($output -join "`n").Trim()
}

function Escape-PythonString {
    param([string]$Value)
    return $Value.Replace("\", "\\").Replace("'", "\'")
}

function Write-LocalConfig {
    $databaseDirectory = Join-Path $AppRoot "database"
    New-Item -ItemType Directory -Path $databaseDirectory -Force | Out-Null
    $configFile = Join-Path $databaseDirectory "config_local.py"
    $hostValue = Escape-PythonString $DbHost
    $userValue = Escape-PythonString $DbUser
    $passwordValue = Escape-PythonString $DbPassword
    $databaseValue = Escape-PythonString $DbName
    @"
DB_CONFIG_LOCAL = {
    "host": "$hostValue",
    "port": $DbPort,
    "user": "$userValue",
    "password": "$passwordValue",
    "database": "$databaseValue",
}
"@ | Set-Content -LiteralPath $configFile -Encoding UTF8
}

if (-not $SkipDatabase) {
    if (-not (Test-Path -LiteralPath $SqlFile)) {
        throw "No se encontró el archivo SQL: $SqlFile"
    }

    $mysqlClient = Find-MySqlClient
    if (-not $mysqlClient) {
        Install-MariaDb
        $mysqlClient = Find-MySqlClient
    }
    if (-not $mysqlClient) {
        throw "MariaDB se instaló, pero no se encontró el cliente mysql/mariadb."
    }

    Start-DatabaseService
    Wait-ForDatabase -HostName $DbHost -Port $DbPort

    $exists = Invoke-MySqlQuery -Client $mysqlClient `
        -Query "SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = '$DbName';"
    if ([int]$exists -eq 0) {
        Write-Host "Creando la base de datos demo desde el archivo SQL..."
        Get-Content -LiteralPath $SqlFile -Raw -Encoding UTF8 |
            & $mysqlClient "--host=$DbHost" "--port=$DbPort" "--user=$DbUser" `
            "--password=$DbPassword" "--default-character-set=utf8mb4"
        if ($LASTEXITCODE -ne 0) {
            throw "No se pudo importar la base de datos desde el archivo SQL."
        }
    } else {
        Write-Host "La base de datos '$DbName' ya existe. No se modificó."
    }
}

Write-LocalConfig
Write-Host ""
Write-Host "DOMIYA quedó configurado."
Write-Host "Ejecutable: $AppRoot\DOMIYA.exe"
Write-Host "Base de datos: $DbName en $DbHost`:$DbPort"
