"""Módulos del rol domiciliario: solicitudes disponibles, mis solicitudes y registrar incidente."""
from tkinter import ttk, messagebox

from database.conexion import ErrorBD
from interfaces.panel_base import PanelBase
from interfaces.componentes import TablaDatos, mostrar_error
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
        ttk.Button(barra, text="Tomar solicitud seleccionada", style="Accion.TButton",
                   command=self._tomar).pack(side="left")
        ttk.Button(barra, text="Actualizar", style="Secundario.TButton",
                   command=self._recargar).pack(side="left", padx=8)

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
        ttk.Button(barra, text="Marcar En curso", style="Accion.TButton",
                   command=lambda: self._cambiar(3, "En curso")).pack(side="left")
        ttk.Button(barra, text="Marcar Finalizada", style="Accion.TButton",
                   command=lambda: self._cambiar(4, "Finalizada")).pack(side="left", padx=8)
        ttk.Button(barra, text="Actualizar", style="Secundario.TButton",
                   command=self._recargar).pack(side="left")

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
        self.cmb_solicitud = ttk.Combobox(marco, values=list(self.solicitudes), state="readonly", width=52)
        self.cmb_solicitud.grid(row=1, column=0, sticky="w", pady=(2, 6))

        ttk.Label(marco, text="Tipo de incidente", style="Campo.TLabel").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.cmb_tipo = ttk.Combobox(marco, values=list(self.tipos), state="readonly", width=52)
        self.cmb_tipo.grid(row=3, column=0, sticky="w", pady=(2, 6))

        ttk.Label(marco, text="Descripción (máx. 50 caracteres)", style="Campo.TLabel").grid(
            row=4, column=0, sticky="w", pady=(6, 0))
        self.ent_desc = ttk.Entry(marco, width=55)
        self.ent_desc.grid(row=5, column=0, sticky="w", pady=(2, 6))

        ttk.Button(marco, text="Registrar incidente", style="Accion.TButton",
                   command=self._registrar).grid(row=6, column=0, sticky="w", pady=(18, 0))

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