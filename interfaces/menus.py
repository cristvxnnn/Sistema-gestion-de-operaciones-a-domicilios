"""Menú lateral de cada rol."""
from interfaces.cliente import (
    PanelResumenCliente, PanelMisSolicitudes, PanelMisIncidentes)
from interfaces.cliente_marketplace import PanelNuevaSolicitudMarketplace
from interfaces.domiciliario import (
    PanelDisponibles, PanelMisSolicitudesDom, PanelRegistrarIncidente)
from interfaces.admin import (
    PanelDashboard, PanelSolicitudesAdmin, PanelConsultas, PanelBarriosAdmin)

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
        ("resumen", "Mi resumen", PanelResumenCliente),
        ("mis_incidentes", "Mis incidentes", PanelMisIncidentes),
    ],
    "domiciliario": [
        ("disponibles", "Solicitudes disponibles", PanelDisponibles),
        ("mis_solicitudes", "Mis solicitudes", PanelMisSolicitudesDom),
        ("incidentes", "Registrar incidente", PanelRegistrarIncidente),
    ],
    "admin": [
        ("dashboard", "Dashboard", PanelDashboard),
        ("solicitudes", "Solicitudes", PanelSolicitudesAdmin),
        ("barrios", "Barrios", PanelBarriosAdmin),
        ("consultas", "Consultas", PanelConsultas),
    ],
}
