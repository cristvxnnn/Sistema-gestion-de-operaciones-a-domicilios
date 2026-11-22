# EntreCali — guía para compartir e instalar

## Qué compartir

Después de ejecutar `build_exe.ps1`, comparte el archivo `dist/EntreCali.zip`. La carpeta incluida contiene `EntreCali.exe`, sus dependencias y la guía. No envíes solo el `.exe`: conserva juntos todos los archivos extraídos.

## Requisitos

- Windows 10 u 11 de 64 bits.
- Una conexión al servidor MySQL donde esté creada la base `proyectofinal`.
- No hace falta instalar Python ni MySQL Workbench en el computador que ejecuta EntreCali.

El ejecutable no contiene MySQL ni una copia de la base de datos. Todos los usuarios deben conectarse a un servidor que esté encendido y sea accesible desde sus computadores.

## Instalación

1. Extrae `EntreCali.zip` en una carpeta local, por ejemplo `Documentos\EntreCali`.
2. Abre `database\config_local.py` con el Bloc de notas.
3. Reemplaza los valores de `host`, `user` y `password` por los datos del servidor MySQL. Conserva `port` y `database` salvo que el administrador de la base indique otros valores.
4. Guarda el archivo y ejecuta `EntreCali.exe`.

`localhost` o `127.0.0.1` solo funciona si MySQL está instalado en ese mismo computador. Para que varias personas compartan los mismos datos, configura en cada copia el nombre o la IP del mismo servidor MySQL y una cuenta que tenga acceso a `proyectofinal`.

## Conexión entre computadores

- En una red local, usa la IP privada del computador que hospeda MySQL y verifica que los otros equipos puedan alcanzarlo.
- Fuera de esa red, usa una red privada/VPN o un servidor administrado accesible para el grupo.
- El servidor MySQL debe aceptar conexiones desde los computadores autorizados y su puerto debe estar permitido por la red.
- Evita publicar MySQL directamente en Internet. No distribuyas una configuración que contenga una contraseña personal o administrativa; crea una cuenta para la demo y comparte sus datos solo con el grupo.

Si la barra inferior indica que no hay conexión, confirma que el servidor esté activo, que el host/puerto sean correctos y que la cuenta tenga permisos sobre `proyectofinal`.

## Reconstruir el paquete desde el proyecto

En el computador de desarrollo, instala las dependencias de `requirements-build.txt` y ejecuta `build_exe.ps1` desde PowerShell. El resultado compartible queda en `dist/EntreCali.zip`; cada instalación recibe una configuración de ejemplo y debe completar sus propios datos de conexión.
