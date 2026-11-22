# Instalación de DOMIYA en Windows

## Compilar el ejecutable

En el computador de desarrollo:

```powershell
python -m pip install -r requirements-build.txt
.\build_exe.ps1
```

El resultado queda en `dist`:

- `DOMIYA.exe`
- `instalar_domiya.ps1`
- `README_INSTALACION.md`
- `database\SQL proyectoFinal.sql`

## Instalar en otro computador

1. Copia completa la carpeta `dist`.
2. Abre PowerShell como administrador dentro de esa carpeta.
3. Permite scripts solo para esa sesión:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

4. Ejecuta el instalador:

```powershell
.\instalar_domiya.ps1 -DbUser root -DbPassword root
```

El script:

- Busca MariaDB o MySQL.
- Si no existe, intenta instalar MariaDB mediante `winget`.
- Inicia el servicio de base de datos.
- Crea `proyectofinal`.
- Importa `database\SQL proyectoFinal.sql`.
- Genera `database\config_local.py`.

Después abre `DOMIYA.exe`.

Si el computador no tiene `winget`, instala MariaDB manualmente y vuelve a
ejecutar el script con las credenciales configuradas.

## Notas

- El SQL actual contiene datos demo, usuarios, solicitudes e incidentes.
- Si la base ya existe, el instalador no la sobrescribe.
- Cada computador tendrá su propia base local; no compartirá datos con otros
  computadores.
- `config_local.py` contiene la contraseña y no debe subirse al repositorio.
- Para una instalación empresarial conviene crear un usuario de base de datos
  exclusivo para DOMIYA en lugar de usar `root`.
