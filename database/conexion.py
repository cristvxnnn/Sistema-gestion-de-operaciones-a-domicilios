import mysql.connector
from mysql.connector import Error

from database.config import DB_CONFIG


class ErrorBD(Exception):
    """Error de base de datos con un mensaje legible (incluye los SIGNAL de los triggers)."""


def mensaje_error_mysql(error):
    """Traduce errores comunes de MySQL a mensajes útiles para la demo."""
    numero = getattr(error, "errno", None)
    mensaje = str(getattr(error, "msg", error))
    if numero == 1062:
        if "correo" in mensaje.casefold() or "email" in mensaje.casefold():
            return "Ese correo electrónico ya está registrado. Prueba con otro."
        return "Ya existe un registro con esos datos. Verifica la identificación."
    mensajes = {
        1048: "Falta completar un dato obligatorio. Revisa los campos e inténtalo de nuevo.",
        1406: "Uno de los datos supera la longitud permitida. Acórtalo e inténtalo de nuevo.",
        1451: "No se puede eliminar este registro porque tiene información relacionada.",
        1452: "Una opción seleccionada ya no está disponible. Actualiza la pantalla e inténtalo de nuevo.",
        1205: "La base de datos está ocupada. Espera un momento e inténtalo de nuevo.",
        1213: "La operación coincidió con otra actualización. Inténtalo nuevamente.",
    }
    return mensajes.get(numero, mensaje)


def obtener_conexion():
    try:
        return mysql.connector.connect(charset="utf8mb4", **DB_CONFIG)
    except Error as e:
        raise ErrorBD(f"No se pudo conectar a MySQL: {mensaje_error_mysql(e)}") from e


def ejecutar_consulta(sql, params=None):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        filas = cursor.fetchall()
        cursor.close()
        return filas
    except Error as e:
        raise ErrorBD(mensaje_error_mysql(e)) from e
    finally:
        conexion.close()


def ejecutar_comando(sql, params=None):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute(sql, params or ())
        conexion.commit()
        afectadas = cursor.rowcount
        cursor.close()
        return afectadas
    except Error as e:
        conexion.rollback()
        raise ErrorBD(mensaje_error_mysql(e)) from e
    finally:
        conexion.close()


def llamar_procedimiento(nombre, args=()):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.callproc(nombre, list(args))
        resultados = []
        for r in cursor.stored_results():
            columnas = r.column_names
            resultados.append([dict(zip(columnas, fila)) for fila in r.fetchall()])
        conexion.commit()
        cursor.close()
        return resultados
    except Error as e:
        conexion.rollback()
        raise ErrorBD(mensaje_error_mysql(e)) from e
    finally:
        conexion.close()


def probar_conexion():
    """Devuelve (ok, mensaje)."""
    try:
        fila = ejecutar_consulta("SELECT DATABASE() AS bd, VERSION() AS version")[0]
        return True, f"{fila['bd']} (MySQL {fila['version']})"
    except ErrorBD as e:
        return False, str(e)


if __name__ == "__main__":
    print(probar_conexion())
