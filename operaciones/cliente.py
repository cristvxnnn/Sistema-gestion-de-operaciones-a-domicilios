"""Operaciones del rol cliente: sus solicitudes, incidentes y creación de solicitudes."""
from database.conexion import ejecutar_consulta, ejecutar_comando, llamar_procedimiento


def listar_solicitudes(id_cliente):
    return ejecutar_consulta(
        "SELECT s.numeroSolicitud, s.fechaCreacion, s.horaCreacion, "
        "fn_calcular_franja(s.horaCreacion) AS franja, s.descripcion, "
        "COALESCE(est.nombre, CONCAT(s.viaPrincipalExterna, ' ', s.numeroExterno)) AS recogida, "
        "s.montoTotal, m.nombreMetodoPago AS metodoPago, e.nombreEstado AS estado "
        "FROM solicitud s "
        "JOIN estadoSolicitud e ON s.idEstadoSolicitud = e.idEstadoSolicitud "
        "JOIN metodoPago m ON s.idMetodoPago = m.idMetodoPago "
        "LEFT JOIN establecimiento est ON s.codigoEstablecimiento = est.codigoEstablecimiento "
        "WHERE s.identificacionCliente = %s "
        "ORDER BY s.fechaCreacion DESC, s.horaCreacion DESC", (id_cliente,))


def listar_incidentes(id_cliente):
    return ejecutar_consulta(
        "SELECT i.codigoIncidente, i.numeroSolicitud, t.nombreTipoIncidente AS tipo, "
        "i.descripcion, i.fecha, i.hora "
        "FROM incidente i "
        "JOIN tipoIncidente t ON i.idTipoIncidente = t.idTipoIncidente "
        "JOIN solicitud s ON i.numeroSolicitud = s.numeroSolicitud "
        "WHERE s.identificacionCliente = %s "
        "ORDER BY i.fecha DESC, i.hora DESC", (id_cliente,))


def resumen_por_estado(id_cliente):
    return ejecutar_consulta(
        "SELECT e.nombreEstado AS estado, COUNT(s.numeroSolicitud) AS total "
        "FROM estadoSolicitud e "
        "LEFT JOIN solicitud s ON s.idEstadoSolicitud = e.idEstadoSolicitud "
        "AND s.identificacionCliente = %s "
        "GROUP BY e.idEstadoSolicitud, e.nombreEstado "
        "ORDER BY e.idEstadoSolicitud", (id_cliente,))


def total_gastado(id_cliente):
    """Suma de las solicitudes Finalizadas (estado 4)."""
    fila = ejecutar_consulta(
        "SELECT IFNULL(SUM(montoTotal), 0) AS total FROM solicitud "
        "WHERE identificacionCliente = %s AND idEstadoSolicitud = 4", (id_cliente,))[0]
    return fila["total"]


def cancelar_solicitud(numero, id_cliente):
    """UPDATE a estado Cancelada (5). El trigger control_estado_solicitud valida el cambio."""
    return ejecutar_comando(
        "UPDATE solicitud SET idEstadoSolicitud = 5 "
        "WHERE numeroSolicitud = %s AND identificacionCliente = %s", (numero, id_cliente))


def listar_metodos_pago():
    return ejecutar_consulta(
        "SELECT idMetodoPago, nombreMetodoPago FROM metodoPago "
        "WHERE nombreMetodoPago <> 'Ninguno' ORDER BY idMetodoPago")


def listar_tipos_recogida():
    return ejecutar_consulta(
        "SELECT idTipoRecogida, nombreTipoRecogida FROM tipoRecogida ORDER BY idTipoRecogida")


def listar_establecimientos():
    return ejecutar_consulta(
        "SELECT codigoEstablecimiento, nombre FROM establecimiento ORDER BY nombre")


def siguiente_numero_solicitud():
    fila = ejecutar_consulta(
        "SELECT IFNULL(MAX(numeroSolicitud), 1000) + 1 AS siguiente FROM solicitud")[0]
    return int(fila["siguiente"])


def crear_solicitud(id_cliente, d):
    """Llama al procedimiento crear_solicitud (valida y deja la solicitud en estado Creada)."""
    numero = siguiente_numero_solicitud()
    llamar_procedimiento("crear_solicitud", (
        numero, id_cliente, d["descripcion"], d["monto"], d["idMetodoPago"],
        d["via"], d["numeroExterno"], d["idBarrio"],
        d["codigoEstablecimiento"], d["idTipoRecogida"]))
    return numero