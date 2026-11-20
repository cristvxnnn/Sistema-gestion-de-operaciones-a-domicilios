"""Componentes reutilizables: tabla de datos, tarjetas de indicadores y aviso de error."""
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from tkinter import ttk


def formatear(valor):
    if valor is None:
        return ""
    if isinstance(valor, timedelta):            # las columnas TIME llegan como timedelta
        total = int(valor.total_seconds())
        return f"{total // 3600:02d}:{(total % 3600) // 60:02d}"
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d %H:%M")
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, time):
        return valor.strftime("%H:%M")
    if isinstance(valor, Decimal):
        return f"${valor:,.0f}"
    return str(valor)


class TablaDatos(ttk.Frame):
    """Treeview con barra de desplazamiento. columnas = [(clave, titulo, ancho), ...]"""

    def __init__(self, parent, columnas, alto=12):
        super().__init__(parent, style="Contenido.TFrame")
        self.columnas = columnas
        self._filas = []
        self.arbol = ttk.Treeview(self, columns=[c[0] for c in columnas],
                                  show="headings", height=alto, selectmode="browse")
        for clave, titulo, ancho in columnas:
            self.arbol.heading(clave, text=titulo)
            self.arbol.column(clave, width=ancho, anchor="w")
        barra = ttk.Scrollbar(self, orient="vertical", command=self.arbol.yview)
        self.arbol.configure(yscrollcommand=barra.set)
        self.arbol.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

    def cargar(self, filas):
        self._filas = list(filas)
        self.arbol.delete(*self.arbol.get_children())
        for i, fila in enumerate(self._filas):
            self.arbol.insert("", "end", iid=str(i),
                              values=[formatear(fila.get(c[0])) for c in self.columnas])

    def seleccionada(self):
        sel = self.arbol.selection()
        return self._filas[int(sel[0])] if sel else None


def tarjeta_indicador(parent, titulo, valor):
    tarjeta = ttk.Frame(parent, style="Tarjeta.TFrame", padding=18)
    ttk.Label(tarjeta, text=titulo, style="TarjetaTexto.TLabel").pack(anchor="w")
    ttk.Label(tarjeta, text=str(valor), style="TarjetaTitulo.TLabel",
              font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(6, 0))
    return tarjeta


def mostrar_error(parent, error):
    tarjeta = ttk.Frame(parent, style="Tarjeta.TFrame", padding=24)
    tarjeta.pack(fill="x")
    ttk.Label(tarjeta, text="No se pudieron cargar los datos",
              style="TarjetaTitulo.TLabel").pack(anchor="w")
    ttk.Label(tarjeta, text=str(error), style="TarjetaTexto.TLabel",
              wraplength=700, justify="left").pack(anchor="w", pady=(4, 0))