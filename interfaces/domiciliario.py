"""Módulos del rol domiciliario: solicitudes disponibles, mis solicitudes y registrar incidente."""
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox

from database.conexion import ErrorBD
from interfaces.estilos import COLORES
from interfaces.panel_base import PanelBase
from interfaces.componentes import (
    TablaDatos, mostrar_error, limitar_campo, combo_estilizado,
    boton_estilizado, entrada_estilizada, entrada_busqueda,
    ejecutar_en_segundo_plano, normalizar_busqueda)
from interfaces.validaciones import MAX_TEXTO_SQL
from operaciones import domiciliario as op


class PanelDisponibles(PanelBase):
    TITULO = "Solicitudes disponibles"
    DESCRIPCION = "Solicitudes creadas que puedes tomar."

    COLUMNAS = [
        ("numeroSolicitud", "N°", 60), ("fechaCreacion", "Fecha", 90),
        ("horaCreacion", "Hora", 60), ("franja", "Franja", 120),
        ("cliente", "Cliente", 140), ("descripcion", "Descripción", 170),
        ("recogida", "Recogida", 140), ("montoTotal", "Monto", 90),
        ("metodoPago", "Pago", 90),
    ]

    def construir(self):
        barra = ttk.Frame(self.contenido, style="Contenido.TFrame")
        barra.pack(fill="x", pady=(0, 10))
        self.btn_tomar = boton_estilizado(
            barra, "Tomar solicitud seleccionada", self._tomar)
        self.btn_tomar.configure(state="disabled")
        self.btn_tomar.pack(side="left")
        self.btn_actualizar = boton_estilizado(
            barra, "Actualizar", self._recargar, primario=False)
        self.btn_actualizar.pack(side="left", padx=8)
        self.lbl_total = ttk.Label(barra, text="", style="Subtitulo.TLabel")
        self.lbl_total.pack(side="right")
        self.ent_busqueda = entrada_busqueda(barra, self._buscar, ancho=230)
        self.ent_busqueda.pack(side="right", padx=10)

        self.tabla = TablaDatos(self.contenido, self.COLUMNAS)
        self.tabla.pack(fill="both", expand=True)
        self.tabla.arbol.bind("<<TreeviewSelect>>", self._actualizar_accion)
        self.solicitudes = []
        self._recargar()

    def _recargar(self):
        self.btn_actualizar.configure(state="disabled")
        self.btn_tomar.configure(state="disabled")
        self.lbl_total.configure(text="Actualizando…")
        ejecutar_en_segundo_plano(
            self, op.listar_disponibles, self._cargar_solicitudes,
            self._fallo_recarga)

    def _cargar_solicitudes(self, filas):
        self.btn_actualizar.configure(state="normal")
        self.solicitudes = filas
        self._buscar(self.ent_busqueda.get())

    def _fallo_recarga(self, error):
        self.btn_actualizar.configure(state="normal")
        self.lbl_total.configure(text="No se pudieron cargar las solicitudes")
        messagebox.showerror("Error de base de datos", str(error))

    def _buscar(self, texto):
        consulta = normalizar_busqueda(texto)
        filas = [fila for fila in self.solicitudes if not consulta or consulta in
                 normalizar_busqueda(" ".join(
                     str(valor) for valor in fila.values()))]
        self.tabla.cargar(filas)
        self.lbl_total.configure(
            text=f"{len(filas)} de {len(self.solicitudes)} solicitud(es)")
        self.btn_tomar.configure(state="disabled")

    def _actualizar_accion(self, _evento=None):
        habilitado = self.tabla.seleccionada() is not None
        self.btn_tomar.configure(state="normal" if habilitado else "disabled")

    def _tomar(self):
        fila = self.tabla.seleccionada()
        if fila is None:
            messagebox.showinfo("Selecciona una solicitud", "Elige una solicitud de la tabla.")
            return
        numero = fila["numeroSolicitud"]
        self.btn_tomar.configure(state="disabled")
        self.btn_actualizar.configure(state="disabled")
        self.lbl_total.configure(text=f"Asignando solicitud {numero}…")
        ejecutar_en_segundo_plano(
            self,
            lambda: op.tomar_solicitud(
                numero, self.ventana.sesion["identificacion"]),
            lambda _resultado: self._toma_completada(numero),
            self._toma_fallida)

    def _toma_completada(self, numero):
        messagebox.showinfo(
            "Solicitud asignada", f"La solicitud {numero} quedó asignada a ti.")
        self._recargar()

    def _toma_fallida(self, error):
        messagebox.showerror("No se pudo tomar la solicitud", str(error))
        self._recargar()


class PanelMisSolicitudesDom(PanelBase):
    TITULO = "Mis solicitudes"
    DESCRIPCION = "Solicitudes que tienes asignadas."

    COLUMNAS = [
        ("numeroSolicitud", "N°", 60), ("fechaCreacion", "Fecha", 90),
        ("cliente", "Cliente", 140), ("descripcion", "Descripción", 170),
        ("recogida", "Recogida", 140), ("montoTotal", "Monto", 90),
        ("metodoPago", "Pago", 90), ("estado", "Estado", 90),
    ]

    def construir(self):
        barra = ttk.Frame(self.contenido, style="Contenido.TFrame")
        barra.pack(fill="x", pady=(0, 10))
        self.btn_en_curso = boton_estilizado(
            barra, "Marcar En curso",
            lambda: self._cambiar(3, "En curso"))
        self.btn_en_curso.configure(state="disabled")
        self.btn_en_curso.pack(side="left")
        self.btn_finalizada = boton_estilizado(
            barra, "Marcar Finalizada",
            lambda: self._cambiar(4, "Finalizada"), primario=False)
        self.btn_finalizada.configure(state="disabled")
        self.btn_finalizada.pack(side="left", padx=8)
        self.btn_actualizar = boton_estilizado(
            barra, "Actualizar", self._recargar, primario=False)
        self.btn_actualizar.pack(side="left")
        self.lbl_total = ttk.Label(barra, text="", style="Subtitulo.TLabel")
        self.lbl_total.pack(side="right")
        self.ent_busqueda = entrada_busqueda(barra, self._buscar, ancho=210)
        self.ent_busqueda.pack(side="right", padx=10)

        self.tabla = TablaDatos(self.contenido, self.COLUMNAS)
        self.tabla.pack(fill="both", expand=True)
        self.tabla.arbol.bind("<<TreeviewSelect>>", self._actualizar_acciones)
        self.solicitudes = []
        self._recargar()

    def _recargar(self):
        self.btn_actualizar.configure(state="disabled")
        self.btn_en_curso.configure(state="disabled")
        self.btn_finalizada.configure(state="disabled")
        self.lbl_total.configure(text="Actualizando…")
        ejecutar_en_segundo_plano(
            self,
            lambda: op.listar_mis_solicitudes(
                self.ventana.sesion["identificacion"]),
            self._cargar_solicitudes, self._fallo_recarga)

    def _cargar_solicitudes(self, filas):
        self.btn_actualizar.configure(state="normal")
        self.solicitudes = filas
        self._buscar(self.ent_busqueda.get())

    def _fallo_recarga(self, error):
        self.btn_actualizar.configure(state="normal")
        self.lbl_total.configure(text="No se pudieron cargar las solicitudes")
        messagebox.showerror("Error de base de datos", str(error))

    def _buscar(self, texto):
        consulta = normalizar_busqueda(texto)
        filas = [fila for fila in self.solicitudes if not consulta or consulta in
                 normalizar_busqueda(" ".join(
                     str(valor) for valor in fila.values()))]
        self.tabla.cargar(filas)
        self.lbl_total.configure(
            text=f"{len(filas)} de {len(self.solicitudes)} solicitud(es)")
        self._actualizar_acciones()

    def _actualizar_acciones(self, _evento=None):
        fila = self.tabla.seleccionada()
        estado = str(fila.get("estado", "")).casefold() if fila else ""
        self.btn_en_curso.configure(
            state="normal" if estado == "asignada" else "disabled")
        self.btn_finalizada.configure(
            state="normal" if estado == "en curso" else "disabled")

    def _cambiar(self, nuevo_estado, nombre):
        fila = self.tabla.seleccionada()
        if fila is None:
            messagebox.showinfo("Selecciona una solicitud", "Elige una solicitud de la tabla.")
            return
        numero = fila["numeroSolicitud"]
        if nuevo_estado == 4 and not messagebox.askyesno(
                "Finalizar domicilio",
                f"¿Confirmas que la solicitud {numero} fue entregada?\n\n"
                "Al finalizarla, este cambio quedará registrado en el historial."):
            return
        self.btn_en_curso.configure(state="disabled")
        self.btn_finalizada.configure(state="disabled")
        self.btn_actualizar.configure(state="disabled")
        self.lbl_total.configure(text=f"Actualizando solicitud {numero}…")
        ejecutar_en_segundo_plano(
            self,
            lambda: op.cambiar_estado(
                numero, self.ventana.sesion["identificacion"], nuevo_estado),
            lambda afectadas: self._cambio_completado(numero, nombre, afectadas),
            self._cambio_fallido)

    def _cambio_completado(self, numero, nombre, afectadas):
        if afectadas == 0:
            messagebox.showinfo("Sin cambios", f"La solicitud {numero} ya estaba en ese estado.")
        else:
            messagebox.showinfo("Listo", f"La solicitud {numero} ahora está {nombre}.")
        self._recargar()

    def _cambio_fallido(self, error):
        messagebox.showerror("No se pudo cambiar el estado", str(error))
        self._recargar()


class PanelHistorialDomiciliario(PanelBase):
    TITULO = "Mi historial"
    DESCRIPCION = "Revisa tus entregas finalizadas y el estado de tus solicitudes."

    ESTADOS = {
        "Creada": "#F4B740",
        "Asignada": "#4F83CC",
        "En curso": "#F58220",
        "Finalizada": "#20A675",
        "Cancelada": "#D66B75",
    }

    def construir(self):
        self.lbl_cargando = ctk.CTkLabel(
            self.contenido, text="Cargando tu historial…",
            text_color=COLORES["texto_suave"], font=("Segoe UI", 12))
        self.lbl_cargando.pack(anchor="w", padx=8, pady=10)
        ejecutar_en_segundo_plano(
            self,
            lambda: op.listar_mis_solicitudes(
                self.ventana.sesion["identificacion"]),
            self._mostrar_historial, self._fallo_historial)

    def _fallo_historial(self, error):
        self.lbl_cargando.destroy()
        mostrar_error(self.contenido, error)

    def _mostrar_historial(self, solicitudes):
        self.lbl_cargando.destroy()
        self.solicitudes = solicitudes
        conteos = {estado: sum(
            str(fila.get("estado", "")).casefold() == estado.casefold()
            for fila in solicitudes) for estado in self.ESTADOS}

        resumen = ctk.CTkFrame(self.contenido, fg_color="transparent")
        resumen.pack(fill="x", pady=(0, 14))
        for columna in range(4):
            resumen.grid_columnconfigure(columna, weight=1, uniform="resumen_dom")
        tarjetas = [
            ("Entregas finalizadas", conteos["Finalizada"], "#E7F6EF", "#16845F"),
            ("En curso", conteos["En curso"], "#FFF0E1", COLORES["acento"]),
            ("Asignadas", conteos["Asignada"], "#EAF2FF", "#3A6FB5"),
            ("Solicitudes gestionadas", len(solicitudes), "#F0EDFA", "#6654A3"),
        ]
        for indice, (titulo, valor, fondo, acento) in enumerate(tarjetas):
            tarjeta = ctk.CTkFrame(
                resumen, fg_color=fondo, corner_radius=14)
            tarjeta.grid(row=0, column=indice, sticky="ew",
                          padx=(0 if indice == 0 else 8, 0), pady=2)
            ctk.CTkLabel(
                tarjeta, text=titulo, text_color=COLORES["texto_suave"],
                font=("Segoe UI", 10), anchor="w").pack(
                    anchor="w", padx=14, pady=(12, 2))
            ctk.CTkLabel(
                tarjeta, text=str(valor), text_color=acento,
                font=("Segoe UI", 21, "bold"), anchor="w").pack(
                    anchor="w", padx=14, pady=(0, 12))

        panel_grafico = ctk.CTkFrame(
            self.contenido, fg_color=COLORES["tarjeta"], corner_radius=14,
            border_width=1, border_color=COLORES["borde"])
        panel_grafico.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(
            panel_grafico, text="Estado de tus solicitudes",
            text_color=COLORES["texto"], font=("Segoe UI", 14, "bold"),
            anchor="w").pack(anchor="w", padx=16, pady=(12, 2))
        ctk.CTkLabel(
            panel_grafico, text="Distribución de los domicilios que has gestionado.",
            text_color=COLORES["texto_suave"], font=("Segoe UI", 10),
            anchor="w").pack(anchor="w", padx=16)
        grafico_fila = ctk.CTkFrame(panel_grafico, fg_color="transparent")
        grafico_fila.pack(fill="x", padx=14, pady=(4, 10))
        pastel = tk.Canvas(
            grafico_fila, width=170, height=150, bg=COLORES["tarjeta"],
            highlightthickness=0)
        pastel.pack(side="left", padx=(8, 20))
        self._dibujar_grafico(pastel, conteos, len(solicitudes))
        leyenda = ctk.CTkFrame(grafico_fila, fg_color="transparent")
        leyenda.pack(side="left", fill="both", expand=True)
        for estado, color in self.ESTADOS.items():
            fila = ctk.CTkFrame(leyenda, fg_color="transparent")
            fila.pack(fill="x", pady=2)
            ctk.CTkLabel(fila, text="●", text_color=color,
                         font=("Segoe UI", 13)).pack(side="left", padx=(0, 7))
            ctk.CTkLabel(fila, text=estado, text_color=COLORES["texto_suave"],
                         font=("Segoe UI", 10)).pack(side="left")
            ctk.CTkLabel(fila, text=str(conteos[estado]), text_color=COLORES["texto"],
                         font=("Segoe UI", 10, "bold")).pack(side="right", padx=10)

        encabezado_lista = ctk.CTkFrame(self.contenido, fg_color="transparent")
        encabezado_lista.pack(fill="x", pady=(0, 7))
        ctk.CTkLabel(
            encabezado_lista, text="Entregas finalizadas",
            text_color=COLORES["texto"], font=("Segoe UI", 16, "bold"),
            anchor="w").pack(side="left")
        self.lbl_total_historial = ctk.CTkLabel(
            encabezado_lista, text="", text_color=COLORES["texto_suave"],
            font=("Segoe UI", 10))
        self.lbl_total_historial.pack(side="right")
        self.busqueda_historial = ctk.CTkEntry(
            self.contenido, height=36, corner_radius=9,
            border_color=COLORES["borde"], fg_color=COLORES["tarjeta"],
            placeholder_text="Buscar por solicitud o destino…")
        self.busqueda_historial.pack(fill="x", pady=(0, 8))
        self.busqueda_historial.bind("<KeyRelease>", self._filtrar_historial)
        self.lista_finalizadas = ctk.CTkScrollableFrame(
            self.contenido, fg_color=COLORES["fondo"], corner_radius=12,
            scrollbar_button_color=COLORES["borde"],
            scrollbar_button_hover_color=COLORES["acento"])
        self.lista_finalizadas.pack(fill="both", expand=True)
        self.lista_finalizadas.grid_columnconfigure(0, weight=1)
        self._filtrar_historial()

    @staticmethod
    def _dibujar_grafico(canvas, conteos, total):
        x0, y0, x1, y1 = 15, 8, 145, 138
        if not total:
            canvas.create_oval(x0, y0, x1, y1, fill="#E9EEF5", outline="")
            centro = 0
        else:
            inicio = 90
            for estado, color in PanelHistorialDomiciliario.ESTADOS.items():
                cantidad = conteos[estado]
                if cantidad:
                    extension = 360 * cantidad / total
                    canvas.create_arc(
                        x0, y0, x1, y1, start=inicio, extent=extension,
                        fill=color, outline=COLORES["tarjeta"], width=2,
                        style=tk.PIESLICE)
                    inicio -= extension
            centro = total
        canvas.create_oval(48, 41, 112, 105, fill=COLORES["tarjeta"], outline="")
        canvas.create_text(80, 65, text=str(centro), fill=COLORES["texto"],
                           font=("Segoe UI", 17, "bold"))
        canvas.create_text(80, 84, text="total", fill=COLORES["texto_suave"],
                           font=("Segoe UI", 8))

    def _filtrar_historial(self, _evento=None):
        for widget in self.lista_finalizadas.winfo_children():
            widget.destroy()
        texto = normalizar_busqueda(self.busqueda_historial.get())
        filas = [fila for fila in self.solicitudes
                 if str(fila.get("estado", "")).casefold() == "finalizada"
                 and (not texto or texto in normalizar_busqueda(" ".join(
                     str(fila.get(campo, "")) for campo in
                     ("numeroSolicitud", "descripcion", "recogida", "fechaCreacion"))))]
        self.lbl_total_historial.configure(
            text=f"{len(filas)} entrega(s)" if filas else "")
        if not filas:
            mensaje = ("No hay entregas que coincidan con la búsqueda." if texto else
                       "Tus entregas finalizadas aparecerán aquí.")
            ctk.CTkLabel(
                self.lista_finalizadas, text=mensaje, height=70,
                fg_color=COLORES["tarjeta"], text_color=COLORES["texto_suave"],
                corner_radius=12).grid(row=0, column=0, sticky="ew", pady=4)
            return
        for indice, fila in enumerate(filas):
            tarjeta = ctk.CTkFrame(
                self.lista_finalizadas, fg_color=COLORES["tarjeta"],
                corner_radius=12, border_width=1, border_color=COLORES["borde"])
            tarjeta.grid(row=indice, column=0, sticky="ew", pady=4)
            tarjeta.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                tarjeta,
                text=f"Solicitud #{fila['numeroSolicitud']} · {fila.get('descripcion') or 'Domicilio'}",
                text_color=COLORES["texto"], font=("Segoe UI", 11, "bold"),
                anchor="w").grid(row=0, column=0, sticky="ew", padx=14, pady=(9, 2))
            ctk.CTkLabel(
                tarjeta, text=f"{fila.get('fechaCreacion', '')} · {fila.get('recogida', '')}",
                text_color=COLORES["texto_suave"], font=("Segoe UI", 10),
                anchor="w").grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 9))
            ctk.CTkLabel(
                tarjeta, text="✓ Finalizada", text_color=self.ESTADOS["Finalizada"],
                font=("Segoe UI", 10, "bold")).grid(
                    row=0, column=1, rowspan=2, padx=14)


class PanelRegistrarIncidente(PanelBase):
    TITULO = "Registrar incidente"
    DESCRIPCION = "Reporta una novedad en una solicitud asignada o en curso."

    def construir(self):
        self.lbl_cargando = ttk.Label(
            self.contenido, text="Cargando solicitudes y tipos de incidente…",
            style="Subtitulo.TLabel")
        self.lbl_cargando.pack(anchor="w", padx=12, pady=12)
        ejecutar_en_segundo_plano(
            self, lambda: self._consultar(self.ventana.sesion["identificacion"]),
            self._mostrar_formulario, self._fallo_carga)

    @staticmethod
    def _consultar(identificacion):
        solicitudes = op.listar_activas(identificacion)
        op.asegurar_tipo_incidente_otro()
        return solicitudes, op.listar_tipos_incidente()

    def _fallo_carga(self, error):
        self.lbl_cargando.destroy()
        mostrar_error(self.contenido, error)

    def _mostrar_formulario(self, resultado):
        self.lbl_cargando.destroy()
        solicitudes, tipos = resultado

        if not solicitudes:
            tarjeta = ttk.Frame(self.contenido, style="Tarjeta.TFrame", padding=24)
            tarjeta.pack(fill="x")
            ttk.Label(tarjeta, text="No tienes solicitudes asignadas o en curso.",
                      style="TarjetaTitulo.TLabel").pack(anchor="w")
            ttk.Label(tarjeta, text="Toma una solicitud en «Solicitudes disponibles» para poder reportar incidentes.",
                      style="TarjetaTexto.TLabel").pack(anchor="w", pady=(4, 0))
            return

        self.solicitudes = {f"{f['numeroSolicitud']} — {f['descripcion']} ({f['estado']})":
                            f["numeroSolicitud"] for f in solicitudes}
        self.tipos = {f["nombreTipoIncidente"]: f["idTipoIncidente"] for f in tipos}

        marco = ttk.Frame(self.contenido, style="Tarjeta.TFrame", padding=24)
        marco.pack(fill="both", expand=True)
        marco.grid_columnconfigure(0, weight=1)

        ttk.Label(marco, text="Solicitud", style="Campo.TLabel").grid(row=0, column=0, sticky="w", pady=(6, 0))
        self.cmb_solicitud = combo_estilizado(
            marco, list(self.solicitudes), ancho=560)
        self.cmb_solicitud.grid(row=1, column=0, sticky="ew", pady=(4, 10))

        ttk.Label(marco, text="Tipo de incidente", style="Campo.TLabel").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.cmb_tipo = combo_estilizado(
            marco, list(self.tipos), ancho=560,
            comando=self._cambiar_tipo)
        self.cmb_tipo.grid(row=3, column=0, sticky="ew", pady=(4, 10))

        self.lbl_desc = ttk.Label(marco, text="Descripción (máx. 50 caracteres)",
                                  style="Campo.TLabel")
        self.lbl_desc.grid(
            row=4, column=0, sticky="w", pady=(6, 0))
        self.ent_desc = entrada_estilizada(
            marco, ancho=560, placeholder="Describe brevemente el incidente")
        self.ent_desc.grid(row=5, column=0, sticky="ew", pady=(4, 6))
        limitar_campo(self.ent_desc, MAX_TEXTO_SQL)
        self.lbl_contador = ttk.Label(
            marco, text=f"0/{MAX_TEXTO_SQL} caracteres",
            style="TarjetaTexto.TLabel")
        self.lbl_contador.grid(row=6, column=0, sticky="e")
        self.ent_desc.bind("<KeyRelease>", self._actualizar_contador, add="+")

        self.lbl_error_incidente = ttk.Label(
            marco, text="", style="Error.TLabel", wraplength=650)
        self.lbl_error_incidente.grid(row=7, column=0, sticky="w", pady=(8, 0))

        self.btn_registrar = boton_estilizado(
            marco, "Registrar incidente", self._registrar)
        self.btn_registrar.configure(height=44)
        self.btn_registrar.grid(row=8, column=0, sticky="ew", pady=(12, 0))

    def _actualizar_contador(self, _evento=None):
        cantidad = len(self.ent_desc.get())
        color = "#B42318" if cantidad >= MAX_TEXTO_SQL else COLORES["texto_suave"]
        self.lbl_contador.configure(
            text=f"{cantidad}/{MAX_TEXTO_SQL} caracteres", foreground=color)

    def _cambiar_tipo(self, _evento=None):
        if self.cmb_tipo.get().casefold() == "otro":
            self.lbl_desc.configure(text="¿Cuál fue el incidente? (máx. 50 caracteres)")
        else:
            self.lbl_desc.configure(text="Descripción (máx. 50 caracteres)")

    def _registrar(self):
        desc = self.ent_desc.get().strip()
        if not self.cmb_solicitud.get() or not self.cmb_tipo.get() or not desc:
            self.lbl_error_incidente.configure(
                text="Completa la solicitud, el tipo de incidente y la descripción.")
            return
        if len(desc) > 50:
            self.lbl_error_incidente.configure(
                text="La descripción admite máximo 50 caracteres.")
            return
        self.lbl_error_incidente.configure(text="")
        numero = self.solicitudes[self.cmb_solicitud.get()]
        id_tipo = self.tipos[self.cmb_tipo.get()]
        self.btn_registrar.configure(state="disabled", text="Registrando…")
        ejecutar_en_segundo_plano(
            self,
            lambda: self._guardar_incidente(id_tipo, desc, numero),
            lambda resultado: self._incidente_registrado(numero, resultado),
            self._fallo_registro)

    @staticmethod
    def _guardar_incidente(id_tipo, descripcion, numero):
        codigo = op.registrar_incidente(id_tipo, descripcion, numero)
        return codigo, op.estado_solicitud(numero)

    def _incidente_registrado(self, numero, resultado):
        codigo, estado = resultado
        messagebox.showinfo("Incidente registrado",
                            f"Incidente {codigo} registrado.\nEstado actual de la solicitud {numero}: {estado}.")
        self.ventana.mostrar_modulo("incidentes")  # recarga la lista de solicitudes activas

    def _fallo_registro(self, error):
        self.btn_registrar.configure(state="normal", text="Registrar incidente")
        self.lbl_error_incidente.configure(text=f"No se pudo registrar: {error}")
