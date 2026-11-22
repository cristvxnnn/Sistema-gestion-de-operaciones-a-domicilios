"""Menú lateral de cada rol."""
from interfaces.cliente import (
    PanelResumenCliente, PanelMisSolicitudes)
from interfaces.cliente_marketplace import PanelNuevaSolicitudMarketplace
from interfaces.domiciliario import (
    PanelDisponibles, PanelMisSolicitudesDom, PanelHistorialDomiciliario,
    PanelRegistrarIncidente)
from interfaces.admin import (
    PanelDashboard, PanelSolicitudesAdmin, PanelIncidentesAdmin,
    PanelUsuariosAdmin, PanelEstablecimientosAdmin,
    PanelConsultas, PanelBarriosAdmin)

TITULOS_ROL = {
    "cliente": "Cliente",
    "domiciliario": "Domiciliario",
    "admin": "Administrador",
}

# rol -> lista de (clave, texto del menú, clase del panel)
MENUS = {
    "cliente": [
        ("nueva_solicitud", "Crear solicitud", PanelNuevaSolicitudMarketplace),
        ("mis_solicitudes", "Mis solicitudes", PanelMisSolicitudes),
        ("resumen", "Mi historial", PanelResumenCliente),
    ],
    "domiciliario": [
        ("disponibles", "Solicitudes disponibles", PanelDisponibles),
        ("mis_solicitudes", "Mis solicitudes", PanelMisSolicitudesDom),
        ("historial", "Mi historial", PanelHistorialDomiciliario),
        ("incidentes", "Registrar incidente", PanelRegistrarIncidente),
    ],
    "admin": [
        ("dashboard", "Dashboard", PanelDashboard),
        ("solicitudes", "Solicitudes", PanelSolicitudesAdmin),
        ("incidentes_admin", "Incidentes", PanelIncidentesAdmin),
        ("usuarios", "Usuarios", PanelUsuariosAdmin),
        ("establecimientos", "Establecimientos", PanelEstablecimientosAdmin),
        ("barrios", "Barrios", PanelBarriosAdmin),
        ("consultas", "Consultas", PanelConsultas),
    ],
}
