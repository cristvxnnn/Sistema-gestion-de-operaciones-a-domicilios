"""Clase base de los módulos: título, descripción y área de contenido."""
import customtkinter as ctk
from tkinter import ttk
from interfaces.estilos import COLORES


class PanelBase(ctk.CTkFrame):
    TITULO = ""
    DESCRIPCION = ""
    MENSAJE_PENDIENTE = "Este módulo se implementará en las siguientes etapas."

    def __init__(self, parent, ventana=None):
        super().__init__(
            parent, fg_color=COLORES["fondo"], corner_radius=0)
        self.ventana = ventana  # VentanaPrincipal (sesión y navegación)

        encabezado = ctk.CTkFrame(self, fg_color="transparent")
        encabezado.pack(fill="x", padx=30, pady=(26, 0))
        ctk.CTkLabel(
            encabezado, text=self.TITULO, text_color=COLORES["texto"],
            font=("Segoe UI", 25, "bold"), anchor="w").pack(anchor="w")
        ctk.CTkLabel(
            encabezado, text=self.DESCRIPCION,
            text_color=COLORES["texto_suave"],
            font=("Segoe UI", 12), anchor="w").pack(anchor="w", pady=(3, 0))

        self.contenido = ttk.Frame(self, style="Contenido.TFrame")
        self.contenido.pack(
            fill="both", expand=True, padx=30, pady=(20, 26))
        self.construir()  # se ejecuta cada vez que se entra al módulo (datos frescos)

    def construir(self):
        tarjeta = ttk.Frame(self.contenido, style="Tarjeta.TFrame", padding=24)
        tarjeta.pack(fill="x")
        ttk.Label(tarjeta, text="En desarrollo", style="TarjetaTitulo.TLabel").pack(anchor="w")
        ttk.Label(tarjeta, text=self.MENSAJE_PENDIENTE,
                  style="TarjetaTexto.TLabel").pack(anchor="w", pady=(4, 0))


def panel_pendiente(titulo, descripcion):
    return type("PanelPendiente", (PanelBase,),
                {"TITULO": titulo, "DESCRIPCION": descripcion})
