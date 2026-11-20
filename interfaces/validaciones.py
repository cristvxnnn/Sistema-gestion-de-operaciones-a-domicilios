"""Validaciones y límites compartidos por los formularios de la aplicación."""
import re


MAX_TEXTO_SQL = 50
MIN_IDENTIFICACION = 6
MAX_IDENTIFICACION = 10
MAX_BIGINT = 19


def limitar_entry(entry, maximo=MAX_TEXTO_SQL, solo_numeros=False):
    """Impide escribir más caracteres de los aceptados por el campo."""
    def validar(propuesto):
        if len(propuesto) > maximo:
            return False
        if solo_numeros and propuesto and not propuesto.isdigit():
            return False
        return True

    comando = entry.register(validar)
    entry.configure(validate="key", validatecommand=(comando, "%P"))
    return entry


def motivo_correo_invalido(correo):
    """Devuelve un mensaje específico o None si el correo parece válido."""
    texto = correo.strip()
    if not texto:
        return "El correo electrónico es obligatorio."
    if len(texto) > MAX_TEXTO_SQL:
        return f"El correo electrónico admite máximo {MAX_TEXTO_SQL} caracteres."
    if any(caracter.isspace() for caracter in texto):
        return "El correo electrónico no puede contener espacios."
    if "@" not in texto:
        return "Al correo le falta el símbolo «@»."
    if texto.count("@") != 1:
        return "El correo debe contener un solo símbolo «@»."

    usuario, dominio = texto.split("@")
    if not usuario:
        return "Debes escribir el nombre del usuario antes de «@»."
    if usuario.startswith(".") or usuario.endswith(".") or ".." in usuario:
        return "La parte anterior a «@» no puede tener puntos consecutivos o extremos."
    if not dominio:
        return "Debes escribir un dominio después de «@»."
    if dominio.startswith(".") or dominio.endswith("."):
        return "El dominio no puede empezar ni terminar con un punto."
    if ".." in dominio:
        return "El dominio no puede contener dos puntos seguidos."
    if "." not in dominio:
        return "El dominio debe incluir una extensión, por ejemplo «.com»."
    if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+", usuario):
        return "La parte anterior a «@» contiene caracteres no válidos."
    if not re.fullmatch(r"[A-Za-z0-9.-]+", dominio):
        return "El dominio contiene caracteres no válidos."
    return None


def validar_identificacion(texto):
    """Valida la longitud y el formato de una identificación."""
    if not texto:
        return "La identificación es obligatoria."
    if not texto.isdigit():
        return "La identificación debe contener solo números."
    if len(texto) < MIN_IDENTIFICACION:
        return f"La identificación debe tener mínimo {MIN_IDENTIFICACION} dígitos."
    if len(texto) > MAX_IDENTIFICACION:
        return f"La identificación no puede superar {MAX_IDENTIFICACION} dígitos."
    return None
