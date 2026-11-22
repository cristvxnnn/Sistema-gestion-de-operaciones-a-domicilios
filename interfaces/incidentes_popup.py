"""Ventana emergente del historial de incidentes del cliente."""
import customtkinter as ctk

from interfaces.componentes import ejecutar_en_segundo_plano
from interfaces.estilos import COLORES
from operaciones import cliente as operaciones_cliente


class PopupIncidentes(ctk.CTkToplevel):
    ANCHO = 440
    ALTO = 560

    def __init__(self, parent, identificacion):
        super().__init__(parent.winfo_toplevel())
        self.parent_panel = parent
        self.identificacion = identificacion
        self.title("Incidentes")
        self.configure(fg_color=COLORES["fondo"])
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.overrideredirect(True)
        self._posicionar(parent.btn_incidentes)

        contenedor = ctk.CTkFrame(
            self, fg_color=COLORES["tarjeta"], corner_radius=16,
            border_width=1, border_color=COLORES["borde"])
        contenedor.pack(fill="both", expand=True, padx=2, pady=2)

        encabezado = ctk.CTkFrame(contenedor, fg_color="transparent")
        encabezado.pack(fill="x", padx=18, pady=(16, 12))
        encabezado.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            encabezado, text="🔔", width=40, height=40, corner_radius=12,
            fg_color=COLORES["acento_claro"], text_color=COLORES["acento"],
            font=("Segoe UI Emoji", 19)).grid(row=0, column=0, rowspan=2, padx=(0, 10))
        ctk.CTkLabel(
            encabezado, text="Incidentes", text_color=COLORES["texto"],
            font=("Segoe UI", 17, "bold"), anchor="w").grid(
                row=0, column=1, sticky="sw")
        self.lbl_total = ctk.CTkLabel(
            encabezado, text="Cargando historial…", text_color=COLORES["texto_suave"],
            font=("Segoe UI", 10), anchor="w")
        self.lbl_total.grid(row=1, column=1, sticky="nw")
        ctk.CTkButton(
            encabezado, text="×", width=30, height=30, corner_radius=9,
            fg_color="transparent", hover_color=COLORES["acento_claro"],
            text_color=COLORES["texto_suave"], font=("Segoe UI", 18),
            command=self.destroy).grid(row=0, column=2, rowspan=2, padx=(8, 0))

        ctk.CTkFrame(
            contenedor, height=1, fg_color=COLORES["borde"],
            corner_radius=0).pack(fill="x", padx=18)
        ctk.CTkLabel(
            contenedor, text="Historial de reportes", text_color=COLORES["texto"],
            font=("Segoe UI", 12, "bold"), anchor="w").pack(
                fill="x", padx=18, pady=(12, 8))

        self.lista = ctk.CTkScrollableFrame(
            contenedor, fg_color=COLORES["fondo"], corner_radius=12)
        self.lista.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.lista.grid_columnconfigure(0, weight=1)

        self.bind("<Escape>", lambda _evento: self.destroy())
        parent.bind("<Destroy>", self._cerrar_con_panel, add="+")
        ejecutar_en_segundo_plano(
            self,
            lambda: operaciones_cliente.listar_incidentes(self.identificacion),
            self._mostrar_incidentes, self._mostrar_error)

    def _cerrar_con_panel(self, evento):
        if evento.widget is self.parent_panel and self.winfo_exists():
            self.destroy()

    def _posicionar(self, boton):
        self.update_idletasks()
        x_objetivo = boton.winfo_rootx() + boton.winfo_width() - self.ANCHO
        y_objetivo = boton.winfo_rooty() + boton.winfo_height() + 8
        x = max(8, min(x_objetivo, self.winfo_screenwidth() - self.ANCHO - 8))
        y = min(y_objetivo, self.winfo_screenheight() - self.ALTO - 48)
        self.geometry(f"{self.ANCHO}x{self.ALTO}+{x}+{max(8, y)}")
        self.lift()
        self.focus_force()

    def _mostrar_error(self, error):
        self.lbl_total.configure(text="No se pudo cargar el historial")
        self._mostrar_estado_vacio(f"Error al consultar los incidentes: {error}")

    def _mostrar_incidentes(self, incidentes):
        self.lbl_total.configure(
            text=f"{len(incidentes)} incidente(s) reportado(s)")
        if not incidentes:
            self._mostrar_estado_vacio("Aún no se han reportado incidentes en tus solicitudes.")
            return

        for indice, incidente in enumerate(incidentes):
            tarjeta = ctk.CTkFrame(
                self.lista, fg_color=COLORES["tarjeta"], corner_radius=12,
                border_width=1, border_color=COLORES["borde"])
            tarjeta.grid(row=indice, column=0, sticky="ew", padx=3, pady=5)
            tarjeta.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                tarjeta, text="Se reportó un incidente",
                text_color=COLORES["texto"], font=("Segoe UI", 12, "bold"),
                anchor="w").grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 2))
            ctk.CTkLabel(
                tarjeta,
                text=f"Solicitud #{incidente['numeroSolicitud']}  ·  {incidente['tipo']}",
                text_color=COLORES["acento"], font=("Segoe UI", 10, "bold"),
                anchor="w", wraplength=360).grid(
                    row=1, column=0, sticky="ew", padx=14, pady=(0, 7))

            detalle = ctk.CTkFrame(
                tarjeta, fg_color="#FFF8F1", corner_radius=9)
            detalle.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
            detalle.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                detalle, text=incidente["descripcion"], text_color="#334155",
                font=("Segoe UI", 11), anchor="w", justify="left",
                wraplength=340).grid(row=0, column=0, sticky="ew", padx=10, pady=(9, 4))
            ctk.CTkLabel(
                detalle,
                text=f"{incidente['fecha']}  ·  {incidente['hora']}  ·  Código {incidente['codigoIncidente']}",
                text_color=COLORES["texto_suave"], font=("Segoe UI", 9),
                anchor="w", wraplength=340).grid(
                    row=1, column=0, sticky="ew", padx=10, pady=(0, 9))

    def _mostrar_estado_vacio(self, mensaje):
        estado = ctk.CTkFrame(
            self.lista, fg_color=COLORES["tarjeta"], corner_radius=12,
            border_width=1, border_color=COLORES["borde"])
        estado.grid(row=0, column=0, sticky="ew", padx=3, pady=5)
        ctk.CTkLabel(
            estado, text="🔔", text_color=COLORES["acento"],
            font=("Segoe UI Emoji", 24)).pack(pady=(18, 6))
        ctk.CTkLabel(
            estado, text=mensaje, text_color=COLORES["texto_suave"],
            font=("Segoe UI", 10), wraplength=350, justify="center").pack(
                padx=16, pady=(0, 18))
