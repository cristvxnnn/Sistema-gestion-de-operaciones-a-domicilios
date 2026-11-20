import tkinter as tk
from tkinter import ttk

from interfaces.estilos import aplicar_estilos, COLORES
from interfaces.panel_principal import PanelPrincipal
from interfaces.modulos.usuarios import PanelUsuarios
from interfaces.modulos.clientes import PanelClientes
from interfaces.modulos.domiciliarios import PanelDomiciliarios
from interfaces.modulos.solicitudes import PanelSolicitudes
from interfaces.modulos.incidentes import PanelIncidentes
from interfaces.modulos.consultas import PanelConsultas


MODULOS = [
    ("inicio", "Inicio", PanelPrincipal),
    ("usuarios", "Usuarios", PanelUsuarios),
    ("clientes", "Clientes", PanelClientes),
    ("domiciliarios", "Domiciliarios", PanelDomiciliarios),
    ("solicitudes", "Solicitudes", PanelSolicitudes),
    ("incidentes", "Incidentes", PanelIncidentes),
    ("consultas", "Consultas", PanelConsultas),
]

class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de gestión de operaciones a domicilio")
        self.geometry("1100x660")
        self.minsize(900, 560)
        aplicar_estilos(self)

        self._botones = {}
        self._paneles = {}
        self._actual = None

        self._crear_barra_estado()
        self._crear_menu_lateral()
        self._crear_area_contenido()
        self.mostrar("inicio")

    def _crear_menu_lateral(self):
        menu=ttk.Frame(self, style="Menu.TFrame", width=230)
        menu.pack(side="left", fill="y")
        menu.pack_propagate(False)

        ttk.Label(menu, text="Domicilios", style="Marca.TLabel").pack(anchor="w", padx=18, pady=(22, 0))
        ttk.Label(menu, text="Gestion de operaciones", style="MarcaSub.TLabel").pack(anchor="w", padx=18, pady=(0,20))

        for clave, texto, _ in MODULOS:
            boton=ttk.Button(menu, text=texto, style="Menu.TButton", command=lambda k=clave: self.mostrar(k))
            boton.pack(fill="x")
            self._botones[clave]=boton

        tk.Frame(self, width=1, background=COLORES["borde"]).pack(side="left", fill="y")

    def _crear_area_contenido(self):
        self.area=ttk.Frame(self, style="Menu.TFrame")
        self.area.pack(side="left", fill="both", expand=True)

    def _crear_barra_estado(self):
        barra=ttk.Frame(self, style="Contenido.TFrame")
        barra.pack(side="bottom", fill="x")
        self.lbl_conexion=ttk.Label(barra, text="Base de datos: sin conexion", style="Estado.TLabel")
        self.lbl_conexion.pack(side="left", padx=12, pady=4)

    def mostrar(self, clave):
        if clave not in self._paneles:
            clase = next(c for k, _, c in MODULOS if k == clave)
            self._paneles[clave] = clase(self.area, navegar=self.mostrar)

        if self._actual:
            self._paneles[self._actual].pack_forget()
            self._botones[self._actual].configure(style="Menu.TButton")

        panel = self._paneles[clave]
        panel.pack(fill="both", expand=True)
        self._botones[clave].configure(style="MenuActivo.TButton")
        self._actual = clave
        panel.al_mostrar()

    def actualizar_estado_conexion(self, texto):
        self.lbl_conexion.configure(text=texto)
