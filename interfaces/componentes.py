from datetime import date, datetime, time, timedelta
from decimal import Decimal
from threading import Thread
import tkinter as tk
import unicodedata
from tkinter import ttk
import customtkinter as ctk

from interfaces.estilos import COLORES
from interfaces.validaciones import limitar_entry

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


def normalizar_busqueda(texto):
    normalizado = unicodedata.normalize("NFD", str(texto or "").casefold())
    return "".join(caracter for caracter in normalizado
                   if unicodedata.category(caracter) != "Mn").strip()


class TablaDatos(ttk.Frame):
    """Treeview con barra de desplazamiento. columnas = [(clave, titulo, ancho), ...]"""

    def __init__(self, parent, columnas, alto=12):
        super().__init__(parent, style="Contenido.TFrame")
        self.columnas = columnas
        self._filas = []
        self._todas_las_filas = []
        self.arbol = ttk.Treeview(self, columns=[c[0] for c in columnas],
                                  show="headings", height=alto, selectmode="browse")
        for clave, titulo, ancho in columnas:
            self.arbol.heading(clave, text=titulo)
            self.arbol.column(clave, width=ancho, anchor="w")
        barra = ctk.CTkScrollbar(
            self, orientation="vertical", command=self.arbol.yview,
            width=12, corner_radius=8,
            fg_color=COLORES["fondo"],
            button_color=COLORES["borde"],
            button_hover_color=COLORES["acento"])
        barra_x = ctk.CTkScrollbar(
            self, orientation="horizontal", command=self.arbol.xview,
            height=12, corner_radius=8,
            fg_color=COLORES["fondo"], button_color=COLORES["borde"],
            button_hover_color=COLORES["acento"])
        self.arbol.configure(yscrollcommand=barra.set, xscrollcommand=barra_x.set)
        self.arbol.tag_configure("fila_par", background=COLORES["tarjeta"])
        self.arbol.tag_configure("fila_impar", background="#F7F9FC")
        self.arbol.tag_configure("estado_creada", background="#FFF5D6")
        self.arbol.tag_configure("estado_asignada", background="#EAF2FF")
        self.arbol.tag_configure("estado_en_curso", background="#E8F4FF")
        self.arbol.tag_configure("estado_finalizada", background="#E9F7EF")
        self.arbol.tag_configure("estado_cancelada", background="#FCEBEC")
        self.arbol.tag_configure(
            "fila_vacia", background=COLORES["tarjeta"], foreground=COLORES["texto_suave"])
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.arbol.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")

    def cargar(self, filas):
        self._todas_las_filas = list(filas)
        self.filtrar("")

    def filtrar(self, texto):
        consulta = normalizar_busqueda(texto)
        self._filas = [
            fila for fila in self._todas_las_filas
            if not consulta or consulta in normalizar_busqueda(" ".join(
                formatear(valor) for valor in fila.values()))
        ]
        self.arbol.delete(*self.arbol.get_children())
        if not self._filas and self.columnas:
            valores = ["Sin coincidencias" if consulta else "Sin datos para mostrar"]
            valores.extend("" for _ in self.columnas[1:])
            self.arbol.insert("", "end", iid="__vacio__", values=valores,
                              tags=("fila_vacia",))
        for i, fila in enumerate(self._filas):
            estado = str(fila.get("estado", "")).casefold().replace(" ", "_")
            etiquetas_estado = {
                "creada": "estado_creada",
                "asignada": "estado_asignada",
                "en_curso": "estado_en_curso",
                "finalizada": "estado_finalizada",
                "cancelada": "estado_cancelada",
            }
            etiqueta = etiquetas_estado.get(estado, "fila_par" if i % 2 == 0 else "fila_impar")
            self.arbol.insert("", "end", iid=str(i),
                              values=[formatear(fila.get(c[0])) for c in self.columnas],
                              tags=(etiqueta,))

    def seleccionada(self):
        sel = self.arbol.selection()
        return self._filas[int(sel[0])] if sel and sel[0].isdigit() else None


def tarjeta_indicador(parent, titulo, valor):
    tarjeta = ttk.Frame(parent, style="Tarjeta.TFrame", padding=18)
    ttk.Label(tarjeta, text=titulo, style="TarjetaTexto.TLabel").pack(anchor="w")
    ttk.Label(tarjeta, text=str(valor), style="TarjetaTitulo.TLabel",
              font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(6, 0))
    return tarjeta


def grilla_responsiva(rejilla, tarjetas, ancho):
    """Distribuye tarjetas en cuatro, dos o una columna según el espacio."""
    columnas = 4 if ancho >= 900 else 2 if ancho >= 560 else 1
    if getattr(rejilla, "_columnas_tarjetas", None) == columnas:
        return
    rejilla._columnas_tarjetas = columnas
    for columna in range(4):
        rejilla.columnconfigure(columna, weight=1 if columna < columnas else 0)
    for indice, tarjeta in enumerate(tarjetas):
        tarjeta.grid_forget()
        tarjeta.grid(row=indice // columnas, column=indice % columnas,
                     padx=6, pady=6, sticky="nsew")


def mostrar_error(parent, error):
    tarjeta = ttk.Frame(parent, style="Tarjeta.TFrame", padding=24)
    tarjeta.pack(fill="x")
    ttk.Label(tarjeta, text="No se pudieron cargar los datos",
              style="TarjetaTitulo.TLabel").pack(anchor="w")
    ttk.Label(tarjeta, text=str(error), style="TarjetaTexto.TLabel",
              wraplength=700, justify="left").pack(anchor="w", pady=(4, 0))


def limitar_campo(entry, maximo=50, solo_numeros=False):
    """Aplica a un Entry el límite definido para su columna."""
    return limitar_entry(entry, maximo=maximo, solo_numeros=solo_numeros)


def combo_estilizado(parent, valores, ancho=240, comando=None):
    """Combobox redondeado con la paleta común de la aplicación."""
    return ctk.CTkComboBox(
        parent, values=valores, width=ancho, height=38, corner_radius=9,
        border_width=1, border_color=COLORES["borde"],
        fg_color=COLORES["tarjeta"], button_color=COLORES["acento"],
        button_hover_color="#E66F10", dropdown_fg_color=COLORES["tarjeta"],
        dropdown_hover_color=COLORES["acento_claro"],
        dropdown_text_color=COLORES["texto"], text_color=COLORES["texto"],
        font=("Segoe UI", 11), command=comando, state="readonly")


def boton_estilizado(parent, texto, comando, primario=True):
    """Botón con esquinas suaves y estados hover de la paleta común."""
    return ctk.CTkButton(
        parent, text=texto, command=comando, height=36, corner_radius=9,
        fg_color=COLORES["acento"] if primario else COLORES["tarjeta"],
        hover_color="#E66F10" if primario else COLORES["acento_claro"],
        text_color="#FFFFFF" if primario else COLORES["texto"],
        border_width=0 if primario else 1,
        border_color=COLORES["borde"],
        font=("Segoe UI", 10, "bold"))


def entrada_estilizada(parent, ancho=280, placeholder=""):
    """Campo de texto redondeado, compatible con los límites existentes."""
    return ctk.CTkEntry(
        parent, width=ancho, height=38, corner_radius=9, border_width=1,
        border_color=COLORES["borde"], fg_color=COLORES["tarjeta"],
        text_color=COLORES["texto"], placeholder_text=placeholder,
        font=("Segoe UI", 11))


def entrada_busqueda(parent, comando, ancho=250):
    """Campo de búsqueda compacto para filtrar tablas ya cargadas."""
    campo = ctk.CTkEntry(
        parent, width=ancho, height=36, corner_radius=9, border_width=1,
        border_color=COLORES["borde"], fg_color=COLORES["tarjeta"],
        text_color=COLORES["texto"], placeholder_text="⌕  Buscar…",
        font=("Segoe UI", 11))
    campo.bind("<KeyRelease>", lambda _evento: comando(campo.get()))
    return campo


def ejecutar_en_segundo_plano(widget, tarea, al_completar, al_fallar):
    """Ejecuta trabajo lento sin congelar Tk y entrega resultados al hilo UI."""
    def trabajar():
        try:
            resultado = tarea()
            callback = lambda: al_completar(resultado)
        except Exception as error:
            callback = lambda error=error: al_fallar(error)

        def entregar():
            try:
                if widget.winfo_exists():
                    callback()
            except tk.TclError:
                pass

        try:
            widget.after(0, entregar)
        except (tk.TclError, RuntimeError):
            pass

    Thread(target=trabajar, daemon=True).start()


class GraficoBarras(tk.Canvas):
    def __init__(self, parent, datos, ancho=400, alto=200):
        super().__init__(parent, width=ancho, height=alto,
                         background=COLORES["tarjeta"], highlightthickness=0)
        maximo = max([valor for _, valor in datos] + [1])
        x0, largo = 100, ancho - 150
        paso = alto // max(len(datos), 1)
        for i, (etiqueta, valor) in enumerate(datos):
            y = i * paso + paso // 2
            self.create_text(8, y, text=etiqueta, anchor="w", fill=COLORES["texto"],
                             font=("Segoe UI", 10))
            fin = x0 + largo * valor / maximo
            self.create_rectangle(x0, y - 10, max(fin, x0 + 2), y + 10,
                                  fill=COLORES["acento"], outline="")
            self.create_text(fin + 8, y, text=str(valor), anchor="w",
                             fill=COLORES["texto_suave"], font=("Segoe UI", 10, "bold"))
