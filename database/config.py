import os
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "root"),
    "database": os.getenv("DB_NAME", "proyectofinal"),
}

if getattr(sys, "frozen", False):
    # Keep machine-specific credentials beside the executable, not inside it.
    archivo_local = Path(sys.executable).resolve().parent / "database" / "config_local.py"
    if archivo_local.is_file():
        spec = spec_from_file_location("_domiya_config_local", archivo_local)
        if spec is None or spec.loader is None:
            raise ImportError(f"No se pudo cargar la configuración: {archivo_local}")
        modulo_local = module_from_spec(spec)
        spec.loader.exec_module(modulo_local)
        DB_CONFIG.update(modulo_local.DB_CONFIG_LOCAL)
else:
    try:
        from database.config_local import DB_CONFIG_LOCAL
    except ImportError:
        pass
    else:
        DB_CONFIG.update(DB_CONFIG_LOCAL)
