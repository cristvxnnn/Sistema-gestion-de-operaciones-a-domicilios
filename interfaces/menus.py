from interfaces.panel_base import panel_pendiente
from interfaces.cliente import (PanelResumenCliente, PanelMisSolicitudes, PanelNuevaSolicitud, PanelMisIncidentes)
from interfaces.domiciliario import (PanelDisponibles, PanelMisSolicitudesDom, PanelRegistrarIncidente)
TITULOS_ROL = {
    "cliente": "Cliente",
    "domiciliario": "Domiciliario",
    "admin": "Administrador",
}

# rol -> lista de (clave, texto del menú, clase del panel)
MENUS = {
    "cliente": [
        ("resumen", "Mi resumen", PanelResumenCliente),
        ("mis_solicitudes", "Mis solicitudes", PanelMisSolicitudes),
        ("nueva_solicitud", "Crear solicitud", PanelNuevaSolicitud),
        ("mis_incidentes", "Mis incidentes", PanelMisIncidentes),
    ],
    "domiciliario": [
        ("disponibles", "Solicitudes disponibles", PanelDisponibles),
        ("mis_solicitudes", "Mis solicitudes", PanelMisSolicitudesDom),
        ("incidentes", "Registrar incidente", PanelRegistrarIncidente),
    ],
    "admin": [
        ("dashboard", "Dashboard",
         panel_pendiente("Dashboard", "Resumen general de la operación.")),
        ("solicitudes", "Solicitudes",
         panel_pendiente("Solicitudes", "Todas las solicitudes del sistema.")),
        ("consultas", "Consultas",
         panel_pendiente("Consultas", "Consultas y reportes SQL.")),
    ],
}