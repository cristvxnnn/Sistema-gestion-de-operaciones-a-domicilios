import mysql.connector
from mysql.connector import Error

from database.config import DB_CONFIG


class ErrorBD(Exception):
    """Error de base de datos con un mensaje legible (incluye los SIGNAL de los triggers)."""


def obtener_conexion():
    try:
        return mysql.connector.connect(charset="utf8mb4", **DB_CONFIG)
    except Error as e:
        raise ErrorBD(f"No se pudo conectar a MySQL: {e.msg}") from e


def ejecutar_consulta(sql, params=None):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        filas = cursor.fetchall()
        cursor.close()
        return filas
    except Error as e:
        raise ErrorBD(e.msg) from e
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
        raise ErrorBD(e.msg) from e
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
        raise ErrorBD(e.msg) from e
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