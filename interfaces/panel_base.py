"""Clase base de los módulos: título, descripción y área de contenido."""
import customtkinter as ctk
from tkinter import ttk
from interfaces.componentes import ejecutar_en_segundo_plano
from interfaces.estilos import COLORES
from operaciones import cliente as operaciones_cliente


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
        sesion = getattr(self.ventana, "sesion", None)
        if sesion and sesion.get("rol") == "cliente":
            caja_campana = ctk.CTkFrame(
                encabezado, width=44, height=40, fg_color="transparent")
            caja_campana.pack_propagate(False)
            caja_campana.pack(side="right", anchor="n", padx=(12, 0))
            self.btn_incidentes = ctk.CTkButton(
                caja_campana, text="🔔", width=44, height=40,
                corner_radius=12, fg_color=COLORES["tarjeta"],
                hover_color=COLORES["acento_claro"],
                text_color=COLORES["texto"], border_width=1,
                border_color=COLORES["borde"],
                font=("Segoe UI Emoji", 16),
                command=self._abrir_popup_incidentes)
            self.btn_incidentes.pack(fill="both", expand=True)
            self.dot_incidentes = ctk.CTkFrame(
                caja_campana, width=10, height=10,
                corner_radius=5, fg_color="#E5484D",
                border_width=1, border_color=COLORES["tarjeta"])
            self.dot_incidentes.bind(
                "<Button-1>", lambda _evento: self._abrir_popup_incidentes())
            self.dot_incidentes.place(relx=0.86, rely=0.14, anchor="center")
            self.dot_incidentes.place_forget()
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
        if sesion and sesion.get("rol") == "cliente":
            ejecutar_en_segundo_plano(
                self,
                lambda: operaciones_cliente.listar_incidentes(sesion["identificacion"]),
                self._actualizar_dot_incidentes, lambda _error: None)

    def _actualizar_dot_incidentes(self, incidentes):
        if incidentes:
            self.dot_incidentes.place(relx=0.86, rely=0.14, anchor="center")
        else:
            self.dot_incidentes.place_forget()

    def _abrir_popup_incidentes(self):
        popup = getattr(self.ventana, "_popup_incidentes", None)
        if popup is not None and popup.winfo_exists():
            popup.focus_force()
            return
        from interfaces.incidentes_popup import PopupIncidentes

        self.ventana._popup_incidentes = PopupIncidentes(
            self, self.ventana.sesion["identificacion"])

    def construir(self):
        tarjeta = ttk.Frame(self.contenido, style="Tarjeta.TFrame", padding=24)
        tarjeta.pack(fill="x")
        ttk.Label(tarjeta, text="En desarrollo", style="TarjetaTitulo.TLabel").pack(anchor="w")
        ttk.Label(tarjeta, text=self.MENSAJE_PENDIENTE,
                  style="TarjetaTexto.TLabel").pack(anchor="w", pady=(4, 0))


def panel_pendiente(titulo, descripcion):
    return type("PanelPendiente", (PanelBase,),
                {"TITULO": titulo, "DESCRIPCION": descripcion})
