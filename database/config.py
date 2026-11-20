import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "proyectofinal"),
}

try:
    from database.config_local import DB_CONFIG_LOCAL
    DB_CONFIG.update(DB_CONFIG_LOCAL)
except ImportError:
    pass
