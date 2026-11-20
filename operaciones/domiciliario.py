"""Operaciones del rol domiciliario: tomar solicitudes, cambiar su estado y reportar incidentes."""
from database.conexion import ejecutar_consulta, ejecutar_comando, llamar_procedimiento

_BASE = (
    "SELECT s.numeroSolicitud, s.fechaCreacion, s.horaCreacion, "
    "fn_calcular_franja(s.horaCreacion) AS franja, s.descripcion, "
    "COALESCE(est.nombre, CONCAT(s.viaPrincipalExterna, ' ', s.numeroExterno)) AS recogida, "
    "s.montoTotal, m.nombreMetodoPago AS metodoPago, e.nombreEstado AS estado, "
    "CONCAT(u.nombre, ' ', u.apellidoPaterno) AS cliente "
    "FROM solicitud s "
    "JOIN estadoSolicitud e ON s.idEstadoSolicitud = e.idEstadoSolicitud "
    "JOIN metodoPago m ON s.idMetodoPago = m.idMetodoPago "
    "JOIN usuario u ON s.identificacionCliente = u.identificacion "
    "LEFT JOIN establecimiento est ON s.codigoEstablecimiento = est.codigoEstablecimiento "
)


def listar_disponibles():
    """Solicitudes en estado Creada (1), las más antiguas primero."""
    return ejecutar_consulta(
        _BASE + "WHERE s.idEstadoSolicitud = 1 "
        "ORDER BY s.fechaCreacion, s.horaCreacion")


def listar_mis_solicitudes(id_domiciliario):
    return ejecutar_consulta(
        _BASE + "WHERE s.identificacionDomiciliario = %s "
        "ORDER BY s.fechaCreacion DESC, s.horaCreacion DESC", (id_domiciliario,))


def tomar_solicitud(numero, id_domiciliario):
    """Llama al procedimiento asignar_solicitud (valida estado y domiciliario activo)."""
    llamar_procedimiento("asignar_solicitud", (numero, id_domiciliario))


def cambiar_estado(numero, id_domiciliario, nuevo_estado):
    """UPDATE del estado. El trigger control_estado_solicitud valida la transición."""
    return ejecutar_comando(
        "UPDATE solicitud SET idEstadoSolicitud = %s "
        "WHERE numeroSolicitud = %s AND identificacionDomiciliario = %s",
        (nuevo_estado, numero, id_domiciliario))


def listar_activas(id_domiciliario):
    """Solicitudes Asignadas (2) o En curso (3) del domiciliario."""
    return ejecutar_consulta(
        "SELECT s.numeroSolicitud, s.descripcion, e.nombreEstado AS estado "
        "FROM solicitud s JOIN estadoSolicitud e ON s.idEstadoSolicitud = e.idEstadoSolicitud "
        "WHERE s.identificacionDomiciliario = %s AND s.idEstadoSolicitud IN (2, 3) "
        "ORDER BY s.numeroSolicitud", (id_domiciliario,))


def listar_tipos_incidente():
    return ejecutar_consulta(
        "SELECT idTipoIncidente, nombreTipoIncidente FROM tipoIncidente ORDER BY idTipoIncidente")


def asegurar_tipo_incidente_otro():
    """Crea el tipo Otro si la base inicial todavía no lo contiene."""
    encontrado = ejecutar_consulta(
        "SELECT idTipoIncidente FROM tipoIncidente "
        "WHERE LOWER(nombreTipoIncidente) = 'otro' LIMIT 1")
    if encontrado:
        return int(encontrado[0]["idTipoIncidente"])

    fila = ejecutar_consulta(
        "SELECT COALESCE(MAX(idTipoIncidente), 0) + 1 AS siguiente "
        "FROM tipoIncidente")[0]
    siguiente = int(fila["siguiente"])
    ejecutar_comando(
        "INSERT INTO tipoIncidente (idTipoIncidente, nombreTipoIncidente) "
        "VALUES (%s, %s)", (siguiente, "Otro"))
    return siguiente


def registrar_incidente(id_tipo, descripcion, numero_solicitud):
    """INSERT en incidente. El trigger cambiar_estado_incidente puede cancelar la solicitud."""
    fila = ejecutar_consulta(
        "SELECT IFNULL(MAX(codigoIncidente), 1000) + 1 AS siguiente FROM incidente")[0]
    codigo = int(fila["siguiente"])
    ejecutar_comando(
        "INSERT INTO incidente (codigoIncidente, idTipoIncidente, descripcion, fecha, hora, numeroSolicitud) "
        "VALUES (%s, %s, %s, CURDATE(), CURTIME(), %s)",
        (codigo, id_tipo, descripcion, numero_solicitud))
    return codigo


def estado_solicitud(numero):
    fila = ejecutar_consulta(
        "SELECT e.nombreEstado AS estado FROM solicitud s "
        "JOIN estadoSolicitud e ON s.idEstadoSolicitud = e.idEstadoSolicitud "
        "WHERE s.numeroSolicitud = %s", (numero,))
    return fila[0]["estado"] if fila else ""
