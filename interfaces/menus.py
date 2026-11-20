from interfaces.panel_base import panel_pendiente

TITULOS_ROL = {
    "cliente": "Cliente",
    "domiciliario": "Domiciliario",
    "admin": "Administrador",
}

# rol -> lista de (clave, texto del menú, clase del panel)
MENUS = {
    "cliente": [
        ("resumen", "Mi resumen",
         panel_pendiente("Mi resumen", "Resumen de tu actividad.")),
        ("mis_solicitudes", "Mis solicitudes",
         panel_pendiente("Mis solicitudes", "Historial de tus solicitudes de domicilio.")),
        ("nueva_solicitud", "Crear solicitud",
         panel_pendiente("Crear solicitud", "Registra un nuevo domicilio.")),
        ("mis_incidentes", "Mis incidentes",
         panel_pendiente("Mis incidentes", "Incidentes asociados a tus solicitudes.")),
    ],
    "domiciliario": [
        ("disponibles", "Solicitudes disponibles",
         panel_pendiente("Solicitudes disponibles", "Solicitudes creadas que puedes tomar.")),
        ("mis_solicitudes", "Mis solicitudes",
         panel_pendiente("Mis solicitudes", "Solicitudes que tienes asignadas.")),
        ("incidentes", "Registrar incidente",
         panel_pendiente("Registrar incidente", "Reporta una novedad durante el servicio.")),
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