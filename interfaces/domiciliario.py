"""Módulos del rol domiciliario: solicitudes disponibles, mis solicitudes y registrar incidente."""
from tkinter import ttk, messagebox

from database.conexion import ErrorBD
from interfaces.panel_base import PanelBase
from interfaces.componentes import (
    TablaDatos, mostrar_error, limitar_campo, combo_estilizado,
    boton_estilizado, entrada_estilizada)
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
        boton_estilizado(barra, "Tomar solicitud seleccionada",
                         self._tomar).pack(side="left")
        boton_estilizado(barra, "Actualizar", self._recargar,
                         primario=False).pack(side="left", padx=8)

        self.tabla = TablaDatos(self.contenido, self.COLUMNAS)
        self.tabla.pack(fill="both", expand=True)
        self._recargar()

    def _recargar(self):
        try:
            self.tabla.cargar(op.listar_disponibles())
        except ErrorBD as e:
            messagebox.showerror("Error de base de datos", str(e))

    def _tomar(self):
        fila = self.tabla.seleccionada()
        if fila is None:
            messagebox.showinfo("Selecciona una solicitud", "Elige una solicitud de la tabla.")
            return
        numero = fila["numeroSolicitud"]
        try:
            op.tomar_solicitud(numero, self.ventana.sesion["identificacion"])
        except ErrorBD as e:  # mensajes del procedimiento asignar_solicitud
            messagebox.showerror("No se pudo tomar la solicitud", str(e))
            return
        messagebox.showinfo("Solicitud asignada", f"La solicitud {numero} quedó asignada a ti.")
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
        boton_estilizado(
            barra, "Marcar En curso",
            lambda: self._cambiar(3, "En curso")).pack(side="left")
        boton_estilizado(
            barra, "Marcar Finalizada",
            lambda: self._cambiar(4, "Finalizada")).pack(side="left", padx=8)
        boton_estilizado(barra, "Actualizar", self._recargar,
                         primario=False).pack(side="left")

        self.tabla = TablaDatos(self.contenido, self.COLUMNAS)
        self.tabla.pack(fill="both", expand=True)
        self._recargar()

    def _recargar(self):
        try:
            self.tabla.cargar(op.listar_mis_solicitudes(self.ventana.sesion["identificacion"]))
        except ErrorBD as e:
            messagebox.showerror("Error de base de datos", str(e))

    def _cambiar(self, nuevo_estado, nombre):
        fila = self.tabla.seleccionada()
        if fila is None:
            messagebox.showinfo("Selecciona una solicitud", "Elige una solicitud de la tabla.")
            return
        numero = fila["numeroSolicitud"]
        try:
            afectadas = op.cambiar_estado(numero, self.ventana.sesion["identificacion"], nuevo_estado)
        except ErrorBD as e:  # aquí aparecen los mensajes del trigger
            messagebox.showerror("No se pudo cambiar el estado", str(e))
            return
        if afectadas == 0:
            messagebox.showinfo("Sin cambios", f"La solicitud {numero} ya estaba en ese estado.")
        else:
            messagebox.showinfo("Listo", f"La solicitud {numero} ahora está {nombre}.")
        self._recargar()


class PanelRegistrarIncidente(PanelBase):
    TITULO = "Registrar incidente"
    DESCRIPCION = "Reporta una novedad en una solicitud asignada o en curso."

    def construir(self):
        try:
            solicitudes = op.listar_activas(self.ventana.sesion["identificacion"])
            op.asegurar_tipo_incidente_otro()
            tipos = op.listar_tipos_incidente()
        except ErrorBD as e:
            mostrar_error(self.contenido, e)
            return

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
        marco.pack(anchor="w")

        ttk.Label(marco, text="Solicitud", style="Campo.TLabel").grid(row=0, column=0, sticky="w", pady=(6, 0))
        self.cmb_solicitud = combo_estilizado(
            marco, list(self.solicitudes), ancho=470)
        self.cmb_solicitud.grid(row=1, column=0, sticky="w", pady=(2, 6))

        ttk.Label(marco, text="Tipo de incidente", style="Campo.TLabel").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.cmb_tipo = combo_estilizado(
            marco, list(self.tipos), ancho=470,
            comando=self._cambiar_tipo)
        self.cmb_tipo.grid(row=3, column=0, sticky="w", pady=(2, 6))

        self.lbl_desc = ttk.Label(marco, text="Descripción (máx. 50 caracteres)",
                                  style="Campo.TLabel")
        self.lbl_desc.grid(
            row=4, column=0, sticky="w", pady=(6, 0))
        self.ent_desc = entrada_estilizada(
            marco, ancho=470, placeholder="Describe brevemente el incidente")
        self.ent_desc.grid(row=5, column=0, sticky="w", pady=(2, 6))
        limitar_campo(self.ent_desc, MAX_TEXTO_SQL)

        boton_estilizado(marco, "Registrar incidente", self._registrar).grid(
            row=6, column=0, sticky="w", pady=(18, 0))

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
        try:
            codigo = op.registrar_incidente(self.tipos[self.cmb_tipo.get()], desc, numero)
            estado = op.estado_solicitud(numero)
        except ErrorBD as e:
            messagebox.showerror("No se pudo registrar el incidente", str(e))
            return
        messagebox.showinfo("Incidente registrado",
                            f"Incidente {codigo} registrado.\nEstado actual de la solicitud {numero}: {estado}.")
        self.ventana.mostrar_modulo("incidentes")  # recarga la lista de solicitudes activas
