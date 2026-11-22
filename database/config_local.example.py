"""Copia base para configurar la conexión MySQL de cada instalación."""
DB_CONFIG_LOCAL = {
    # Usa 127.0.0.1 solo cuando MySQL corre en este mismo computador.
    # Para compartir la base de datos, escribe aquí el nombre/IP del servidor.
    "host": "CAMBIAR_POR_HOST_O_IP_DEL_SERVIDOR",
    "port": 3306,
    "user": "CAMBIAR_POR_USUARIO_MYSQL",
    "password": "CAMBIAR_POR_CONTRASENA_MYSQL",
    "database": "proyectofinal",
}
