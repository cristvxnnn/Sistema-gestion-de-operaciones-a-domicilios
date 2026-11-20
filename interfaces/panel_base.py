from tkinter import ttk
from interfaces.estilos import COLORES


class PanelBase(ttk.Frame):
    TITULO = ""
    DESCRIPCION = ""
    MENSAJE_PENDIENTE = "Este módulo se implementara despues"

    def __init__(self, parent, navegar=None):
        super().__init__(parent, style="Contenido.TFrame", padding=28)
        self.navegar = navegar  # función navegar(clave_modulo)

        ttk.Label(self, text=self.TITULO, style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(self, text=self.DESCRIPCION, style="Subtitulo.TLabel").pack(
            anchor="w", pady=(2, 18))

        self.contenido = ttk.Frame(self, style="Contenido.TFrame")
        self.contenido.pack(fill="both", expand=True)
        self.construir()

    def construir(self):
        """Por defecto muestra una tarjeta 'en desarrollo'. Cada módulo la reemplaza."""
        tarjeta = ttk.Frame(self.contenido, style="Tarjeta.TFrame", padding=24)
        tarjeta.pack(fill="x")
        ttk.Label(tarjeta, text="En desarrollo", style="TarjetaTitulo.TLabel").pack(anchor="w")
        ttk.Label(tarjeta, text=self.MENSAJE_PENDIENTE,
                  style="TarjetaTexto.TLabel").pack(anchor="w", pady=(4, 0))

    def al_mostrar(self):
        """Se llama cada vez que el usuario entra al módulo (útil para refrescar datos)."""