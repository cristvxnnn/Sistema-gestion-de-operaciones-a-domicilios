"""Operaciones de ingreso y registro de clientes y domiciliarios."""
import mysql.connector

from database.conexion import ErrorBD, ejecutar_consulta, obtener_conexion


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


def buscar_usuario(identificacion):
    """Devuelve los datos personales compartidos por los distintos roles."""
    filas = ejecutar_consulta(
        "SELECT identificacion, nombre, apellidoPaterno, apellidoMaterno, telefono, correo "
        "FROM usuario WHERE identificacion = %s", (identificacion,))
    return filas[0] if filas else None


def obtener_perfil(identificacion):
    """Obtiene los datos comunes y los datos específicos de cada rol."""
    filas = ejecutar_consulta(
        "SELECT u.identificacion, u.nombre, u.apellidoPaterno, "
        "u.apellidoMaterno, u.telefono, u.correo, "
        "c.identificacion IS NOT NULL AS esCliente, "
        "c.viaPrincipal, c.numero, c.idBarrio, b.nombreBarrio, c.referencia, "
        "d.identificacion IS NOT NULL AS esDomiciliario, "
        "d.codigoDomiciliario, d.idMedioTransporte, "
        "mt.nombreMedioTransporte, d.idEstadoDomiciliario, "
        "ed.nombreEstadoDomiciliario "
        "FROM usuario u "
        "LEFT JOIN cliente c ON c.identificacion = u.identificacion "
        "LEFT JOIN barrio b ON b.idBarrio = c.idBarrio "
        "LEFT JOIN domiciliario d ON d.identificacion = u.identificacion "
        "LEFT JOIN medioTransporte mt "
        "ON mt.idMedioTransporte = d.idMedioTransporte "
        "LEFT JOIN estadoDomiciliario ed "
        "ON ed.idEstadoDomiciliario = d.idEstadoDomiciliario "
        "WHERE u.identificacion = %s",
        (identificacion,))
    return filas[0] if filas else None


def actualizar_perfil(datos):
    """Actualiza datos personales y la información de los roles existentes."""
    conexion = obtener_conexion()
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE usuario SET nombre = %s, apellidoPaterno = %s, "
            "apellidoMaterno = %s, telefono = %s, correo = %s "
            "WHERE identificacion = %s",
            (datos["nombre"], datos["apellidoPaterno"],
             datos["apellidoMaterno"], datos["telefono"], datos["correo"],
             datos["identificacion"]))

        if datos.get("esCliente"):
            cursor.execute(
                "UPDATE cliente SET viaPrincipal = %s, numero = %s, "
                "idBarrio = %s, referencia = %s WHERE identificacion = %s",
                (datos["viaPrincipal"], datos["numero"], datos["idBarrio"],
                 datos["referencia"], datos["identificacion"]))

        if datos.get("esDomiciliario"):
            cursor.execute(
                "UPDATE domiciliario SET idMedioTransporte = %s, "
                "idEstadoDomiciliario = %s WHERE identificacion = %s",
                (datos["idMedioTransporte"], datos["idEstadoDomiciliario"],
                 datos["identificacion"]))

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


def eliminar_cuenta(identificacion, rol_activo):
    """Elimina el rol activo del usuario y borra el usuario solo si no conserva otro rol."""
    conexion = obtener_conexion()
    cursor = None
    try:
        cursor = conexion.cursor()

        if rol_activo == "cliente":
            cursor.execute(
                "SELECT numeroSolicitud FROM solicitud "
                "WHERE identificacionCliente = %s",
                (identificacion,))
            solicitudes = [fila[0] for fila in cursor.fetchall()]
            if solicitudes:
                marcadores = ", ".join(["%s"] * len(solicitudes))
                cursor.execute(
                    f"DELETE FROM incidente WHERE numeroSolicitud IN ({marcadores})",
                    tuple(solicitudes))
                cursor.execute(
                    f"DELETE FROM solicitud WHERE numeroSolicitud IN ({marcadores})",
                    tuple(solicitudes))

            cursor.execute(
                "DELETE FROM cliente WHERE identificacion = %s",
                (identificacion,))

        elif rol_activo == "domiciliario":
            cursor.execute(
                "SELECT COUNT(*) FROM solicitud "
                "WHERE identificacionDomiciliario = %s",
                (identificacion,))
            if cursor.fetchone()[0]:
                raise ErrorBD(
                    "No puedes eliminar tu perfil de domiciliario mientras tengas "
                    "solicitudes asignadas o en historial.")

            cursor.execute(
                "DELETE FROM domiciliario WHERE identificacion = %s",
                (identificacion,))

        # Verifica si aún conserva el otro rol antes de eliminar de usuario
        cursor.execute(
            "SELECT 1 FROM cliente WHERE identificacion = %s "
            "UNION ALL "
            "SELECT 1 FROM domiciliario WHERE identificacion = %s",
            (identificacion, identificacion))
        if cursor.fetchone() is None:
            cursor.execute(
                "DELETE FROM usuario WHERE identificacion = %s",
                (identificacion,))

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

            cursor.execute(
                "UPDATE usuario SET nombre = %s, apellidoPaterno = %s, "
                "apellidoMaterno = %s, telefono = %s, correo = %s "
                "WHERE identificacion = %s",
                (d["nombre"], d["apellidoPaterno"], d["apellidoMaterno"],
                 d["telefono"], d["correo"], d["identificacion"]))
            
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


def registrar_domiciliario(d):
    """Registra un domiciliario nuevo o añade ese rol a un usuario existente."""
    conexion = obtener_conexion()
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT 1 FROM usuario WHERE identificacion = %s",
            (d["identificacion"],))
        usuario_existente = cursor.fetchone() is not None

        cursor.execute(
            "SELECT IFNULL(MAX(codigoDomiciliario), 100) + 1 "
            "FROM domiciliario")
        codigo_domiciliario = int(cursor.fetchone()[0])

        if not usuario_existente:
            cursor.callproc("insertar_domiciliario", [
                d["identificacion"], d["nombre"], d["apellidoPaterno"],
                d["apellidoMaterno"], d["telefono"], d["correo"],
                codigo_domiciliario, d["idMedioTransporte"], 1])
            for resultado in cursor.stored_results():
                resultado.fetchall()
        else:
            cursor.execute(
                "SELECT 1 FROM domiciliario WHERE identificacion = %s",
                (d["identificacion"],))
            if cursor.fetchone() is not None:
                raise ErrorBD("Esta identificación ya está registrada como domiciliario.")

            cursor.execute(
                "UPDATE usuario SET nombre = %s, apellidoPaterno = %s, "
                "apellidoMaterno = %s, telefono = %s, correo = %s "
                "WHERE identificacion = %s",
                (d["nombre"], d["apellidoPaterno"], d["apellidoMaterno"],
                 d["telefono"], d["correo"], d["identificacion"]))
            
            # Usuario ya existe (por ejemplo, como cliente): añadir solo el rol.
            cursor.execute(
                "INSERT INTO domiciliario "
                "(identificacion, codigoDomiciliario, idMedioTransporte, idEstadoDomiciliario) "
                "VALUES (%s, %s, %s, %s)",
                (d["identificacion"], codigo_domiciliario,
                 d["idMedioTransporte"], 1))

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
