"""Preferencias locales de la demo que no pertenecen a la base SQL."""
import json
import os
from pathlib import Path

_memoria = {}


def _ruta_estado():
    carpeta = Path(os.environ.get("APPDATA", Path.home())) / "DOMIYA"
    return carpeta / "incidentes_leidos.json"


def obtener_incidentes_leidos(identificacion):
    clave = str(identificacion)
    try:
        datos = json.loads(_ruta_estado().read_text(encoding="utf-8"))
        guardados = set(map(str, datos.get(clave, []))) if isinstance(datos, dict) else set()
        return guardados | _memoria.get(clave, set())
    except (OSError, ValueError, TypeError):
        return set(_memoria.get(clave, set()))


def marcar_incidentes_leidos(identificacion, incidentes):
    """Guarda los códigos leídos en el perfil local del usuario de Windows."""
    ruta = _ruta_estado()
    clave = str(identificacion)
    try:
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
        except (OSError, ValueError):
            datos = {}
        if not isinstance(datos, dict):
            datos = {}
        leidos = set(map(str, datos.get(clave, [])))
        leidos.update(str(fila["codigoIncidente"]) for fila in incidentes)
        _memoria.setdefault(clave, set()).update(leidos)
        datos[clave] = sorted(leidos)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = ruta.with_suffix(".tmp")
        temporal.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
        temporal.replace(ruta)
        return leidos
    except (OSError, ValueError, TypeError, KeyError):
        # Mantiene la lectura en esta sesión si no puede escribir el archivo local.
        return obtener_incidentes_leidos(identificacion)
