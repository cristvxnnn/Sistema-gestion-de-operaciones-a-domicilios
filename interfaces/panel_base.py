"""Clase base de los módulos: título, descripción y área de contenido."""
from tkinter import ttk


class PanelBase(ttk.Frame):
    TITULO = ""
    DESCRIPCION = ""
    MENSAJE_PENDIENTE = "Este módulo se implementará en las siguientes etapas."

    def __init__(self, parent, ventana=None):
        super().__init__(parent, style="Contenido.TFrame", padding=28)
        self.ventana = ventana  # VentanaPrincipal (sesión y navegación)

        ttk.Label(self, text=self.TITULO, style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(self, text=self.DESCRIPCION, style="Subtitulo.TLabel").pack(
            anchor="w", pady=(2, 18))

        self.contenido = ttk.Frame(self, style="Contenido.TFrame")
        self.contenido.pack(fill="both", expand=True)
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