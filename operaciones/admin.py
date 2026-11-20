"""Operaciones del rol administrador: indicadores, catálogos y consultas."""
from database.conexion import ejecutar_consulta, ejecutar_comando, llamar_procedimiento


def solicitudes_por_estado():
    return ejecutar_consulta(
        "SELECT e.nombreEstado AS estado, COUNT(s.numeroSolicitud) AS total "
        "FROM estadoSolicitud e "
        "LEFT JOIN solicitud s ON s.idEstadoSolicitud = e.idEstadoSolicitud "
        "GROUP BY e.idEstadoSolicitud, e.nombreEstado ORDER BY e.idEstadoSolicitud")


def conteos_generales():
    return ejecutar_consulta(
        "SELECT (SELECT COUNT(*) FROM solicitud) AS solicitudes, "
        "(SELECT COUNT(*) FROM cliente) AS clientes, "
        "(SELECT COUNT(*) FROM domiciliario WHERE idEstadoDomiciliario = 1) AS domiciliariosActivos, "
        "(SELECT COUNT(*) FROM incidente) AS incidentes")[0]


def facturacion():
    """Llama al procedimiento facturacion_total (usa un cursor). Devuelve [efectivo, electrónico, total]."""
    resultados = llamar_procedimiento("facturacion_total")
    return list(resultados[0][0].values())


def solicitudes_recientes(limite=7):
    return ejecutar_consulta(
        "SELECT s.numeroSolicitud, s.fechaCreacion, "
        "CONCAT(u.nombre, ' ', u.apellidoPaterno) AS cliente, s.montoTotal, "
        "e.nombreEstado AS estado "
        "FROM solicitud s "
        "JOIN usuario u ON s.identificacionCliente = u.identificacion "
        "JOIN estadoSolicitud e ON s.idEstadoSolicitud = e.idEstadoSolicitud "
        "ORDER BY s.fechaCreacion DESC, s.horaCreacion DESC LIMIT %s", (limite,))


def listar_estados():
    return ejecutar_consulta(
        "SELECT idEstadoSolicitud, nombreEstado FROM estadoSolicitud ORDER BY idEstadoSolicitud")


def listar_comunas():
    """Devuelve las comunas disponibles para registrar un barrio."""
    return ejecutar_consulta(
        "SELECT idComuna, nombreComuna FROM comuna ORDER BY nombreComuna")


def listar_barrios():
    """Lista barrios con la comuna a la que pertenecen."""
    return ejecutar_consulta(
        "SELECT b.idBarrio, b.nombreBarrio, c.nombreComuna "
        "FROM barrio b JOIN comuna c ON b.idComuna = c.idComuna "
        "ORDER BY c.nombreComuna, b.nombreBarrio")


def crear_barrio(nombre, id_comuna):
    """Registra un barrio nuevo sin permitir duplicados por nombre."""
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre del barrio es obligatorio.")
    if len(nombre) > 50:
        raise ValueError("El nombre del barrio admite máximo 50 caracteres.")
    existente = ejecutar_consulta(
        "SELECT idBarrio FROM barrio WHERE LOWER(nombreBarrio) = LOWER(%s) LIMIT 1",
        (nombre,))
    if existente:
        raise ValueError("Ya existe un barrio con ese nombre.")

    fila = ejecutar_consulta(
        "SELECT COALESCE(MAX(idBarrio), 0) + 1 AS siguiente FROM barrio")[0]
    siguiente = int(fila["siguiente"])
    return ejecutar_comando(
        "INSERT INTO barrio (idBarrio, nombreBarrio, idComuna) VALUES (%s, %s, %s)",
        (siguiente, nombre, id_comuna))


def listar_solicitudes(id_estado=None):
    sql = (
        "SELECT s.numeroSolicitud, s.fechaCreacion, s.horaCreacion, "
        "fn_calcular_franja(s.horaCreacion) AS franja, "
        "CONCAT(uc.nombre, ' ', uc.apellidoPaterno) AS cliente, "
        "CONCAT(ud.nombre, ' ', ud.apellidoPaterno) AS domiciliario, "
        "s.descripcion, "
        "COALESCE(est.nombre, CONCAT(s.viaPrincipalExterna, ' ', s.numeroExterno)) AS recogida, "
        "s.montoTotal, m.nombreMetodoPago AS metodoPago, e.nombreEstado AS estado "
        "FROM solicitud s "
        "JOIN usuario uc ON s.identificacionCliente = uc.identificacion "
        "LEFT JOIN usuario ud ON s.identificacionDomiciliario = ud.identificacion "
        "JOIN estadoSolicitud e ON s.idEstadoSolicitud = e.idEstadoSolicitud "
        "JOIN metodoPago m ON s.idMetodoPago = m.idMetodoPago "
        "LEFT JOIN establecimiento est ON s.codigoEstablecimiento = est.codigoEstablecimiento ")
    params = ()
    if id_estado is not None:
        sql += "WHERE s.idEstadoSolicitud = %s "
        params = (id_estado,)
    sql += "ORDER BY s.fechaCreacion DESC, s.horaCreacion DESC"
    return ejecutar_consulta(sql, params)



CONSULTAS = [
    {"titulo": "Solicitudes con cliente, estado y método de pago",
     "tecnica": "JOIN de cuatro tablas",
     "sql": """SELECT s.numeroSolicitud, u.identificacion AS 'ID cliente', u.nombre, u.apellidoPaterno,
       e.nombreEstado AS 'Estado', m.nombreMetodoPago AS 'Metodo de pago'
FROM solicitud s
JOIN usuario u ON s.identificacionCliente = u.identificacion
JOIN metodoPago m ON s.idMetodoPago = m.idMetodoPago
JOIN estadoSolicitud e ON s.idEstadoSolicitud = e.idEstadoSolicitud"""},
    {"titulo": "Solicitudes y su domiciliario (incluye sin asignar)",
     "tecnica": "LEFT JOIN",
     "sql": """SELECT s.numeroSolicitud, u.identificacion AS 'ID domiciliario', u.nombre, u.apellidoPaterno
FROM solicitud s
LEFT JOIN usuario u ON s.identificacionDomiciliario = u.identificacion"""},
    {"titulo": "Incidentes con tipo, cliente y domiciliario",
     "tecnica": "JOIN",
     "sql": """SELECT i.codigoIncidente, t.nombreTipoIncidente AS 'Tipo incidente', i.numeroSolicitud,
       s.identificacionCliente, s.identificacionDomiciliario
FROM incidente i
JOIN tipoIncidente t ON i.idTipoIncidente = t.idTipoIncidente
JOIN solicitud s ON i.numeroSolicitud = s.numeroSolicitud"""},
    {"titulo": "Total de solicitudes por cliente",
     "tecnica": "LEFT JOIN + GROUP BY + COUNT",
     "sql": """SELECT u.nombre AS 'Nombre cliente', COUNT(s.numeroSolicitud) AS 'Total solicitudes'
FROM cliente c
LEFT JOIN solicitud s ON c.identificacion = s.identificacionCliente
JOIN usuario u ON c.identificacion = u.identificacion
GROUP BY u.identificacion, u.nombre"""},
    {"titulo": "Total vendido por establecimiento",
     "tecnica": "JOIN + GROUP BY + SUM",
     "sql": """SELECT e.nombre AS 'Nombre establecimiento', SUM(s.montoTotal) AS 'Total vendido'
FROM establecimiento e
JOIN solicitud s ON e.codigoEstablecimiento = s.codigoEstablecimiento
GROUP BY e.codigoEstablecimiento, e.nombre"""},
    {"titulo": "Clientes sin solicitudes",
     "tecnica": "Subconsulta con NOT EXISTS",
     "sql": """SELECT c.identificacion, u.nombre AS 'Nombre cliente'
FROM cliente c
JOIN usuario u ON c.identificacion = u.identificacion
WHERE NOT EXISTS (
    SELECT 1 FROM solicitud s WHERE c.identificacion = s.identificacionCliente
)"""},
    {"titulo": "Domiciliarios sin solicitudes asignadas",
     "tecnica": "Subconsulta con NOT IN",
     "sql": """SELECT d.identificacion, u.nombre AS 'Nombre domiciliario'
FROM domiciliario d
JOIN usuario u ON d.identificacion = u.identificacion
WHERE d.identificacion NOT IN (
    SELECT s.identificacionDomiciliario FROM solicitud s
    WHERE d.identificacion = s.identificacionDomiciliario
)"""},
    {"titulo": "Solicitudes sin incidentes",
     "tecnica": "Subconsulta con NOT IN",
     "sql": """SELECT numeroSolicitud AS 'Solicitudes sin incidentes'
FROM solicitud s
WHERE s.numeroSolicitud NOT IN (
    SELECT i.numeroSolicitud FROM incidente i WHERE s.numeroSolicitud = i.numeroSolicitud
)"""},
    {"titulo": "Top 3 clientes en restaurantes y farmacias",
     "tecnica": "Subconsulta IN + GROUP BY + ORDER BY + LIMIT",
     "sql": """SELECT s.identificacionCliente, u.nombre, u.apellidoPaterno,
       COUNT(s.numeroSolicitud) AS 'total pedidos', SUM(s.montoTotal) AS 'monto gastado'
FROM solicitud s
JOIN usuario u ON s.identificacionCliente = u.identificacion
WHERE s.codigoEstablecimiento IN (
    SELECT e.codigoEstablecimiento
    FROM establecimiento e
    JOIN tipoEstablecimiento t ON e.idTipoEstablecimiento = t.idTipoEstablecimiento
    WHERE t.nombreTipoEstablecimiento IN ('Restaurante', 'Farmacia')
)
GROUP BY s.identificacionCliente, u.nombre, u.apellidoPaterno
ORDER BY SUM(s.montoTotal) DESC
LIMIT 3"""},
    {"titulo": "Rol de cada usuario",
     "tecnica": "CASE + LEFT JOIN",
     "sql": """SELECT u.identificacion, u.nombre, u.apellidoPaterno,
    CASE
        WHEN c.identificacion IS NOT NULL AND d.identificacion IS NOT NULL THEN 'Ambos (Cliente y Domiciliario)'
        WHEN c.identificacion IS NOT NULL THEN 'Cliente'
        WHEN d.identificacion IS NOT NULL THEN 'Domiciliario'
        ELSE 'Sin Rol Asignado'
    END AS tipoUsuario
FROM usuario u
LEFT JOIN cliente c ON u.identificacion = c.identificacion
LEFT JOIN domiciliario d ON u.identificacion = d.identificacion"""},
    {"titulo": "Franja horaria de cada solicitud",
     "tecnica": "Función almacenada fn_calcular_franja",
     "sql": """SELECT s.numeroSolicitud, s.identificacionCliente, u.nombre, u.apellidoPaterno AS apellido,
       fn_calcular_franja(s.horaCreacion) AS 'Franja horaria'
FROM solicitud s
JOIN usuario u ON s.identificacionCliente = u.identificacion"""},
    {"titulo": "Facturación total (efectivo y electrónico)",
     "tecnica": "Procedimiento almacenado con cursor",
     "procedimiento": "facturacion_total",
     "sql": "CALL facturacion_total();"},
]


def ejecutar_guardada(consulta):
    """Ejecuta una consulta de CONSULTAS (SELECT o procedimiento) y devuelve lista de diccionarios."""
    if "procedimiento" in consulta:
        resultados = llamar_procedimiento(consulta["procedimiento"])
        return resultados[0] if resultados else []
    return ejecutar_consulta(consulta["sql"])
