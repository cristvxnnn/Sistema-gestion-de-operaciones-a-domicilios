"""Módulos del rol domiciliario: solicitudes disponibles, mis solicitudes y registrar incidente."""
from tkinter import ttk, messagebox
import tkinter as tk
from database.conexion import ErrorBD
from interfaces.estilos import COLORES
from interfaces.panel_base import PanelBase
from interfaces.componentes import (
    TablaDatos, mostrar_error, limitar_campo, combo_estilizado,
    boton_estilizado, entrada_estilizada, entrada_busqueda,
    ejecutar_en_segundo_plano, normalizar_busqueda, grilla_responsiva)
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

        self.btn_registrar = boton_estilizado(
            marco, "Registrar incidente", self._registrar)
        self.btn_registrar.configure(height=44)
        self.btn_registrar.grid(row=7, column=0, sticky="ew", pady=(20, 0))

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
            messagebox.showwarning("Revisa el formulario", "Completa la solicitud, el tipo y la descripción.")
            return
        if len(desc) > 50:
            messagebox.showwarning("Revisa el formulario", "La descripción admite máximo 50 caracteres.")
            return
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
        messagebox.showerror("No se pudo registrar el incidente", str(error))

class PanelResumenDomiciliario(PanelBase):
    TITULO = "Mi historial"
    DESCRIPCION = "Consulta el resumen de tus entregas por estado."

    def construir(self):
        id_domiciliario = self.ventana.sesion["identificacion"]
        self.lbl_cargando = ttk.Label(
            self.contenido, text="Cargando tu resumen…",
            style="Subtitulo.TLabel")
        self.lbl_cargando.pack(anchor="w", padx=12, pady=12)
        ejecutar_en_segundo_plano(
            self, lambda: op.resumen_por_estado(id_domiciliario),
            self._mostrar_resumen, self._fallo_resumen)

    def _fallo_resumen(self, error):
        self.lbl_cargando.destroy()
        mostrar_error(self.contenido, error)

    def _mostrar_resumen(self, estados):
        self.lbl_cargando.destroy()

        indicadores = [("Total de entregas", sum(f["total"] for f in estados))]
        indicadores += [(f["estado"], f["total"]) for f in estados]

        rejilla = ttk.Frame(self.contenido, style="Contenido.TFrame")
        rejilla.pack(fill="x")
        pasteles = ["#EAF2FF", "#FFF3E0", "#E8F8F0", "#F3ECFF", "#FDECEF", "#FFF9DB"]
        tarjetas = []
        for i, (titulo, valor) in enumerate(indicadores):
            color = pasteles[i % len(pasteles)]
            t = tk.Frame(rejilla, bg=color, padx=18, pady=18,
                         highlightbackground="#DCE6F3", highlightthickness=1)
            tk.Label(t, text=titulo, bg=color, fg="#526789",
                     font=("Segoe UI", 10)).pack(anchor="w")
            tk.Label(t, text=str(valor), bg=color, fg="#122B50",
                     font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(6, 0))
            tarjetas.append(t)
        rejilla.bind(
            "<Configure>",
            lambda evento: grilla_responsiva(rejilla, tarjetas, evento.width))
        self.after_idle(lambda: grilla_responsiva(rejilla, tarjetas, rejilla.winfo_width()))