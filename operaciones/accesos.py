"""Operaciones de ingreso y registro de clientes y domiciliarios."""
from database.conexion import ejecutar_consulta, llamar_procedimiento


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
    """Llama al procedimiento insertar_cliente (crea el usuario y el cliente)."""
    llamar_procedimiento("insertar_cliente", (
        d["identificacion"], d["nombre"], d["apellidoPaterno"], d["apellidoMaterno"],
        d["telefono"], d["correo"], d["viaPrincipal"], d["numero"],
        d["idBarrio"], d["referencia"]))


def siguiente_codigo_domiciliario():
    fila = ejecutar_consulta(
        "SELECT IFNULL(MAX(codigoDomiciliario), 100) + 1 AS siguiente FROM domiciliario")[0]
    return int(fila["siguiente"])


def registrar_domiciliario(d):
    llamar_procedimiento("insertar_domiciliario", (
        d["identificacion"], d["nombre"], d["apellidoPaterno"], d["apellidoMaterno"],
        d["telefono"], d["correo"], siguiente_codigo_domiciliario(),
        d["idMedioTransporte"], 1))