from tkinter import ttk
from interfaces.panel_base import PanelBase

ACCESOS=[
    ("usuarios", "Usuarios", "Usuarios y roles del sistema"),
    ("clientes", "Clientes", "Registro y datos de clientes"),
    ("domiciliarios", "Domiciliarios", "Repartidores y su estado"),
    ("solicitudes", "Solicitudes", "Pedidos de domicilio"),
    ("incidentes", "Incidentes", "Reporte y seguimiento de incidentes"),
    ("consultas", "Consultas", "Consultas y reportes del sistema"),

]

class PanelPrincipal(PanelBase):
    TITULO = "Inicio"
    DESCRIPCION = "Sistema de gestión de operaciones a domicilio"

    def construir(self):
        rejilla=ttk.Frame(self.contenido, style="Contenido.TFrame")
        rejilla.pack(fill="both", expand=True)
        columnas=3
        for i in range(columnas):
            rejilla.columnconfigure(i, weight=1, uniform="col")

        for n, (clave, titulo, texto) in enumerate(ACCESOS):
            tarjeta=ttk.Frame(rejilla, style="Tarjeta.TFrame", padding=18)
            tarjeta.grid(row=n//columnas, column=n%columnas, padx=8, pady=8, sticky="nsew")
            ttk.Label(tarjeta, text=titulo, style="TarjetaTitulo.TLabel").pack(anchor="w")
            ttk.Label(tarjeta, text=texto, style="TarjetaTexto.TLabel").pack(anchor="w", pady=(4, 12))
            ttk.Button(tarjeta, text="Ir al módulo", style="Accion.TButton",
                       command=lambda k=clave: self.navegar(k)).pack(anchor="w")