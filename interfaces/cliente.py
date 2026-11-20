"""Módulos del rol cliente: resumen, mis solicitudes, crear solicitud y mis incidentes."""
from decimal import Decimal, InvalidOperation
from tkinter import ttk, messagebox

from database.conexion import ErrorBD
from interfaces.panel_base import PanelBase
from interfaces.componentes import TablaDatos, tarjeta_indicador, mostrar_error
from operaciones import cliente as op
from operaciones.accesos import listar_barrios


class PanelResumenCliente(PanelBase):
    TITULO = "Mi resumen"
    DESCRIPCION = "Resumen de tu actividad."

    def construir(self):
        id_cliente = self.ventana.sesion["identificacion"]
        try:
            estados = op.resumen_por_estado(id_cliente)
            gastado = op.total_gastado(id_cliente)
        except ErrorBD as e:
            mostrar_error(self.contenido, e)
            return

        indicadores = [("Total de solicitudes", sum(f["total"] for f in estados))]
        indicadores += [(f["estado"], f["total"]) for f in estados]
        indicadores.append(("Gastado en finalizadas", f"${gastado:,.0f}"))

        rejilla = ttk.Frame(self.contenido, style="Contenido.TFrame")
        rejilla.pack(fill="x")
        columnas = 4
        for i in range(columnas):
            rejilla.columnconfigure(i, weight=1, uniform="k")
        for n, (titulo, valor) in enumerate(indicadores):
            tarjeta_indicador(rejilla, titulo, valor).grid(
                row=n // columnas, column=n % columnas, padx=6, pady=6, sticky="nsew")


class PanelMisSolicitudes(PanelBase):
    TITULO = "Mis solicitudes"
    DESCRIPCION = "Historial de tus solicitudes de domicilio."

    COLUMNAS = [
        ("numeroSolicitud", "N°", 60), ("fechaCreacion", "Fecha", 90),
        ("horaCreacion", "Hora", 60), ("franja", "Franja", 120),
        ("descripcion", "Descripción", 190), ("recogida", "Recogida", 150),
        ("montoTotal", "Monto", 90), ("metodoPago", "Pago", 90),
        ("estado", "Estado", 90),
    ]

    def construir(self):
        barra = ttk.Frame(self.contenido, style="Contenido.TFrame")
        barra.pack(fill="x", pady=(0, 10))
        ttk.Button(barra, text="Cancelar solicitud seleccionada", style="Accion.TButton",
                   command=self._cancelar).pack(side="left")
        ttk.Button(barra, text="Actualizar", style="Secundario.TButton",
                   command=self._recargar).pack(side="left", padx=8)

        self.tabla = TablaDatos(self.contenido, self.COLUMNAS)
        self.tabla.pack(fill="both", expand=True)
        self._recargar()

    def _recargar(self):
        try:
            self.tabla.cargar(op.listar_solicitudes(self.ventana.sesion["identificacion"]))
        except ErrorBD as e:
            messagebox.showerror("Error de base de datos", str(e))

    def _cancelar(self):
        fila = self.tabla.seleccionada()
        if fila is None:
            messagebox.showinfo("Selecciona una solicitud", "Elige una solicitud de la tabla.")
            return
        numero = fila["numeroSolicitud"]
        if not messagebox.askyesno("Cancelar solicitud", f"¿Cancelar la solicitud {numero}?"):
            return
        try:
            afectadas = op.cancelar_solicitud(numero, self.ventana.sesion["identificacion"])
        except ErrorBD as e:  # aquí aparecen los mensajes del trigger
            messagebox.showerror("No se pudo cancelar", str(e))
            return
        if afectadas == 0:
            messagebox.showinfo("Sin cambios", "La solicitud ya estaba cancelada.")
        else:
            messagebox.showinfo("Listo", f"La solicitud {numero} fue cancelada.")
        self._recargar()


class PanelNuevaSolicitud(PanelBase):
    TITULO = "Crear solicitud"
    DESCRIPCION = "Registra un nuevo domicilio."

    def construir(self):
        try:
            metodos = {f["nombreMetodoPago"]: f["idMetodoPago"] for f in op.listar_metodos_pago()}
            tipos = {f["nombreTipoRecogida"]: f["idTipoRecogida"] for f in op.listar_tipos_recogida()}
            estabs = {f["nombre"]: f["codigoEstablecimiento"] for f in op.listar_establecimientos()}
            barrios = {f["nombreBarrio"]: f["idBarrio"] for f in listar_barrios()}
        except ErrorBD as e:
            mostrar_error(self.contenido, e)
            return
        self.metodos, self.tipos, self.estabs, self.barrios = metodos, tipos, estabs, barrios

        marco = ttk.Frame(self.contenido, style="Tarjeta.TFrame", padding=24)
        marco.pack(anchor="w")

        def etiqueta(texto, fila, col=0, padre=marco):
            ttk.Label(padre, text=texto, style="Campo.TLabel").grid(
                row=fila, column=col, sticky="w", padx=(0, 24), pady=(6, 0))

        etiqueta("Descripción", 0)
        self.ent_desc = ttk.Entry(marco, width=34)
        self.ent_desc.grid(row=1, column=0, sticky="w", padx=(0, 24), pady=(2, 6))
        etiqueta("Monto total ($)", 0, 1)
        self.ent_monto = ttk.Entry(marco, width=20)
        self.ent_monto.grid(row=1, column=1, sticky="w", pady=(2, 6))

        etiqueta("Método de pago", 2)
        self.cmb_metodo = ttk.Combobox(marco, values=list(metodos), state="readonly", width=31)
        self.cmb_metodo.grid(row=3, column=0, sticky="w", padx=(0, 24), pady=(2, 6))
        etiqueta("Tipo de recogida", 2, 1)
        self.cmb_tipo = ttk.Combobox(marco, values=list(tipos), state="readonly", width=17)
        self.cmb_tipo.grid(row=3, column=1, sticky="w", pady=(2, 6))
        self.cmb_tipo.bind("<<ComboboxSelected>>", self._cambiar_tipo)

        # Zona dinámica: establecimiento O dirección externa
        self.marco_est = ttk.Frame(marco, style="Menu.TFrame")
        etiqueta("Establecimiento", 0, 0, self.marco_est)
        self.cmb_est = ttk.Combobox(self.marco_est, values=list(estabs), state="readonly", width=31)
        self.cmb_est.grid(row=1, column=0, sticky="w", pady=(2, 6))

        self.marco_ext = ttk.Frame(marco, style="Menu.TFrame")
        etiqueta("Vía principal (ej. Calle 23)", 0, 0, self.marco_ext)
        self.ent_via = ttk.Entry(self.marco_ext, width=34)
        self.ent_via.grid(row=1, column=0, sticky="w", padx=(0, 24), pady=(2, 6))
        etiqueta("Número (ej. 17-20)", 0, 1, self.marco_ext)
        self.ent_num = ttk.Entry(self.marco_ext, width=20)
        self.ent_num.grid(row=1, column=1, sticky="w", pady=(2, 6))
        etiqueta("Barrio", 2, 0, self.marco_ext)
        self.cmb_barrio = ttk.Combobox(self.marco_ext, values=list(barrios),
                                       state="readonly", width=31)
        self.cmb_barrio.grid(row=3, column=0, sticky="w", pady=(2, 6))

        ttk.Button(marco, text="Crear solicitud", style="Accion.TButton",
                   command=self._crear).grid(row=6, column=0, sticky="w", pady=(18, 0))

    def _cambiar_tipo(self, _evento=None):
        self.marco_est.grid_remove()
        self.marco_ext.grid_remove()
        tipo = self.cmb_tipo.get()
        if tipo == "Establecimiento":
            self.marco_est.grid(row=4, column=0, columnspan=2, sticky="w")
        elif tipo == "Externa":
            self.marco_ext.grid(row=4, column=0, columnspan=2, sticky="w")

    def _leer(self):
        desc = self.ent_desc.get().strip()
        if not desc:
            raise ValueError("La descripción es obligatoria.")
        if len(desc) > 50:
            raise ValueError("La descripción admite máximo 50 caracteres.")
        try:
            monto = Decimal(self.ent_monto.get().strip().replace(",", "."))
        except InvalidOperation:
            raise ValueError("El monto debe ser un número.")
        if monto <= 0:
            raise ValueError("El monto debe ser mayor que cero.")
        if not self.cmb_metodo.get():
            raise ValueError("Selecciona el método de pago.")
        tipo = self.cmb_tipo.get()
        if not tipo:
            raise ValueError("Selecciona el tipo de recogida.")

        datos = {"descripcion": desc, "monto": monto,
                 "idMetodoPago": self.metodos[self.cmb_metodo.get()],
                 "idTipoRecogida": self.tipos[tipo],
                 "codigoEstablecimiento": None, "via": None,
                 "numeroExterno": None, "idBarrio": None}
        if tipo == "Establecimiento":
            if not self.cmb_est.get():
                raise ValueError("Selecciona el establecimiento.")
            datos["codigoEstablecimiento"] = self.estabs[self.cmb_est.get()]
        else:
            via, num = self.ent_via.get().strip(), self.ent_num.get().strip()
            if not via or not num or not self.cmb_barrio.get():
                raise ValueError("Completa la dirección de recogida (vía, número y barrio).")
            datos["via"], datos["numeroExterno"] = via, num
            datos["idBarrio"] = self.barrios[self.cmb_barrio.get()]
        return datos

    def _crear(self):
        try:
            datos = self._leer()
        except ValueError as e:
            messagebox.showwarning("Revisa el formulario", str(e))
            return
        try:
            numero = op.crear_solicitud(self.ventana.sesion["identificacion"], datos)
        except ErrorBD as e:
            messagebox.showerror("No se pudo crear la solicitud", str(e))
            return
        messagebox.showinfo("Solicitud creada", f"Tu solicitud quedó registrada con el número {numero}.")
        self.ventana.mostrar_modulo("mis_solicitudes")


class PanelMisIncidentes(PanelBase):
    TITULO = "Mis incidentes"
    DESCRIPCION = "Incidentes asociados a tus solicitudes."

    COLUMNAS = [
        ("codigoIncidente", "Código", 70), ("numeroSolicitud", "Solicitud", 80),
        ("tipo", "Tipo", 170), ("descripcion", "Descripción", 280),
        ("fecha", "Fecha", 90), ("hora", "Hora", 60),
    ]

    def construir(self):
        tabla = TablaDatos(self.contenido, self.COLUMNAS)
        tabla.pack(fill="both", expand=True)
        try:
            tabla.cargar(op.listar_incidentes(self.ventana.sesion["identificacion"]))
        except ErrorBD as e:
            messagebox.showerror("Error de base de datos", str(e))