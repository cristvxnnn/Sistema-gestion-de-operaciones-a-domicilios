"""Operaciones de ingreso y registro de clientes y domiciliarios."""
import mysql.connector

from database.conexion import ErrorBD, ejecutar_consulta, llamar_procedimiento, obtener_conexion


def buscar_cliente(identificacion):
    filas = ejecutar_consulta(
        "SELECT u.identificacion, u.nombre, u.apellidoPaterno "
        "FROM cliente c JOIN usuario u ON c.identificacion = u.identificacion "
        "WHERE c.identificacion = %s", (identificacion,))
    return filas[0] if filas else None


def buscar_domiciliario(identificacion):
    filas = ejecutar_consulta(
        "SELECT u.identificacion, u.nombre, u.apellidoPaterno "
        "FROM domiciliario d JOIN usuario u ON d.identificacion = u.identificacion "
        "WHERE d.identificacion = %s", (identificacion,))
    return filas[0] if filas else None


def listar_barrios():
    return ejecutar_consulta("SELECT idBarrio, nombreBarrio FROM barrio ORDER BY nombreBarrio")


def listar_medios_transporte():
    return ejecutar_consulta(
        "SELECT idMedioTransporte, nombreMedioTransporte FROM medioTransporte ORDER BY idMedioTransporte")


def registrar_cliente(d):
    """Registra un cliente nuevo o añade ese rol a un usuario existente."""
    conexion = obtener_conexion()
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT 1 FROM usuario WHERE identificacion = %s",
            (d["identificacion"],))
        usuario_existente = cursor.fetchone() is not None

        if not usuario_existente:
            # El procedimiento existente conserva la lógica del alta completa.
            cursor.callproc("insertar_cliente", [
                d["identificacion"], d["nombre"], d["apellidoPaterno"],
                d["apellidoMaterno"], d["telefono"], d["correo"],
                d["viaPrincipal"], d["numero"], d["idBarrio"], d["referencia"]])
            for resultado in cursor.stored_results():
                resultado.fetchall()
        else:
            cursor.execute(
                "SELECT 1 FROM cliente WHERE identificacion = %s",
                (d["identificacion"],))
            if cursor.fetchone() is not None:
                raise ErrorBD("Esta identificación ya está registrada como cliente.")

            # Usuario ya existe (por ejemplo, como domiciliario): añadir solo el rol.
            cursor.execute(
                "INSERT INTO cliente (identificacion, viaPrincipal, numero, idBarrio, referencia) "
                "VALUES (%s, %s, %s, %s, %s)",
                (d["identificacion"], d["viaPrincipal"], d["numero"],
                 d["idBarrio"], d["referencia"]))

        conexion.commit()
    except ErrorBD:
        conexion.rollback()
        raise
    except mysql.connector.Error as e:
        conexion.rollback()
        raise ErrorBD(e.msg) from e
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def siguiente_codigo_domiciliario():
    fila = ejecutar_consulta(
        "SELECT IFNULL(MAX(codigoDomiciliario), 100) + 1 AS siguiente FROM domiciliario")[0]
    return int(fila["siguiente"])


def registrar_domiciliario(d):
    llamar_procedimiento("insertar_domiciliario", (
        d["identificacion"], d["nombre"], d["apellidoPaterno"], d["apellidoMaterno"],
        d["telefono"], d["correo"], siguiente_codigo_domiciliario(),
        d["idMedioTransporte"], 1))
