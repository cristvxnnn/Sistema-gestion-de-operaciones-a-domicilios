"""Módulos del administrador: dashboard, solicitudes y consultas del proyecto."""
import tkinter as tk
from tkinter import ttk, messagebox

from database.conexion import ErrorBD
from interfaces.panel_base import PanelBase
from interfaces.componentes import (
    TablaDatos, GraficoBarras, tarjeta_indicador, mostrar_error, limitar_campo,
    combo_estilizado, boton_estilizado, entrada_estilizada, entrada_busqueda,
    ejecutar_en_segundo_plano, grilla_responsiva)
from interfaces.validaciones import MAX_TEXTO_SQL
from operaciones import admin as op
from operaciones import cliente as op_cliente


class PanelDashboard(PanelBase):
    TITULO = "Dashboard"
    DESCRIPCION = "Resumen general de la operación."

    def construir(self):
        barra = ttk.Frame(self.contenido, style="Contenido.TFrame")
        barra.pack(fill="x", pady=(0, 8))
        self._btn_actualizar = boton_estilizado(
            barra, "Actualizar", self._recargar, primario=False)
        self._btn_actualizar.pack(side="right")
        self.lbl_actualizacion = ttk.Label(
            barra, text="Preparando indicadores…", style="Subtitulo.TLabel")
        self.lbl_actualizacion.pack(side="right", padx=10)
        self.resultados = ttk.Frame(self.contenido, style="Contenido.TFrame")
        self.resultados.pack(fill="both", expand=True)
        self._recargar()

    @staticmethod
    def _consultar():
        return (op.solicitudes_por_estado(), op.conteos_generales(),
                op.facturacion(), op.solicitudes_recientes())

    def _recargar(self):
        self.lbl_actualizacion.configure(text="Actualizando datos…")
        self._btn_actualizar.configure(state="disabled")
        ejecutar_en_segundo_plano(
            self, self._consultar, self._mostrar_datos, self._mostrar_error)

    def _mostrar_error(self, error):
        self.lbl_actualizacion.configure(text="No se pudo actualizar")
        self._btn_actualizar.configure(state="normal")
        for hijo in self.resultados.winfo_children():
            hijo.destroy()
        mostrar_error(self.resultados, error)

    def _mostrar_datos(self, resultado):
        estados, conteos, facturacion, recientes = resultado
        efectivo, electronico, total = facturacion
        for hijo in self.resultados.winfo_children():
            hijo.destroy()

        def dinero(v):
            return f"${v:,.0f}"

        indicadores = [
            ("Solicitudes", conteos["solicitudes"]),
            ("Clientes", conteos["clientes"]),
            ("Domiciliarios activos", conteos["domiciliariosActivos"]),
            ("Incidentes", conteos["incidentes"]),
            ("Facturado en efectivo", dinero(efectivo)),
            ("Facturado electrónico", dinero(electronico)),
            ("Total facturado", dinero(total)),
        ]
        rejilla = ttk.Frame(self.resultados, style="Contenido.TFrame")
        rejilla.pack(fill="x")
        tarjetas = [tarjeta_indicador(rejilla, titulo, valor)
                    for titulo, valor in indicadores]
        rejilla.bind(
            "<Configure>",
            lambda evento: grilla_responsiva(rejilla, tarjetas, evento.width))
        self.after_idle(lambda: grilla_responsiva(rejilla, tarjetas, rejilla.winfo_width()))

        inferior = ttk.Frame(self.resultados, style="Contenido.TFrame")
        inferior.pack(fill="both", expand=True, pady=(10, 0))

        card_graf = ttk.Frame(inferior, style="Tarjeta.TFrame", padding=16)
        card_graf.pack(side="left", anchor="n", padx=(6, 12))
        ttk.Label(card_graf, text="Solicitudes por estado", style="TarjetaTitulo.TLabel").pack(anchor="w")
        GraficoBarras(card_graf, [(f["estado"], f["total"]) for f in estados],
                      ancho=340, alto=190).pack(pady=(8, 0))

        card_tabla = ttk.Frame(inferior, style="Tarjeta.TFrame", padding=16)
        card_tabla.pack(side="left", fill="both", expand=True)
        ttk.Label(card_tabla, text="Solicitudes recientes", style="TarjetaTitulo.TLabel").pack(
            anchor="w", pady=(0, 8))
        tabla = TablaDatos(card_tabla, [
            ("numeroSolicitud", "N°", 50), ("fechaCreacion", "Fecha", 85),
            ("cliente", "Cliente", 130), ("montoTotal", "Monto", 80),
            ("estado", "Estado", 85)], alto=7)
        tabla.pack(fill="both", expand=True)
        tabla.cargar(recientes)
        self.lbl_actualizacion.configure(text="Datos actualizados")
        self._btn_actualizar.configure(state="normal")


class PanelSolicitudesAdmin(PanelBase):
    TITULO = "Solicitudes"
    DESCRIPCION = "Todas las solicitudes del sistema."

    COLUMNAS = [
        ("numeroSolicitud", "N°", 50), ("fechaCreacion", "Fecha", 85),
        ("horaCreacion", "Hora", 55), ("franja", "Franja", 105),
        ("cliente", "Cliente", 120), ("domiciliario", "Domiciliario", 120),
        ("descripcion", "Descripción", 140), ("recogida", "Recogida", 120),
        ("montoTotal", "Monto", 80), ("metodoPago", "Pago", 80),
        ("estado", "Estado", 80),
    ]

    def construir(self):
        try:
            estados = op.listar_estados()
        except ErrorBD as e:
            mostrar_error(self.contenido, e)
            return
        self.estados = {f["nombreEstado"]: f["idEstadoSolicitud"] for f in estados}

        barra = ttk.Frame(self.contenido, style="Contenido.TFrame")
        barra.pack(fill="x", pady=(0, 10))
        ttk.Label(barra, text="Estado:", style="Subtitulo.TLabel").pack(side="left")
        self.cmb_estado = combo_estilizado(
            barra, ["Todos"] + list(self.estados), ancho=190,
            comando=lambda _valor: self._filtrar())
        self.cmb_estado.set("Todos")
        self.cmb_estado.pack(side="left", padx=8)
        self.btn_actualizar = boton_estilizado(
            barra, "Actualizar", self._recargar, primario=False)
        self.btn_actualizar.pack(side="left")
        self.lbl_total = ttk.Label(barra, text="", style="Subtitulo.TLabel")
        self.lbl_total.pack(side="right")
        self.ent_busqueda = entrada_busqueda(barra, self._buscar, ancho=230)
        self.ent_busqueda.pack(side="right", padx=10)

        self.tabla = TablaDatos(self.contenido, self.COLUMNAS)
        self.tabla.pack(fill="both", expand=True)
        self.filas = []
        self._recargar()

    def _recargar(self):
        self.btn_actualizar.configure(state="disabled")
        self.lbl_total.configure(text="Actualizando solicitudes…")
        ejecutar_en_segundo_plano(
            self, op.listar_solicitudes, self._cargar_solicitudes,
            self._fallo_recarga)

    def _cargar_solicitudes(self, filas):
        self.btn_actualizar.configure(state="normal")
        self.filas = filas
        self._filtrar()

    def _fallo_recarga(self, error):
        self.btn_actualizar.configure(state="normal")
        self.lbl_total.configure(text="No se pudieron cargar las solicitudes")
        messagebox.showerror("Error de base de datos", str(error))

    def _filtrar(self, _valor=None):
        estado = self.cmb_estado.get()
        filas = self.filas if estado == "Todos" else [
            fila for fila in self.filas if fila.get("estado") == estado]
        self.tabla.cargar(filas)
        self.tabla.filtrar(self.ent_busqueda.get())
        self._actualizar_total()

    def _buscar(self, texto):
        self.tabla.filtrar(texto)
        self._actualizar_total()

    def _actualizar_total(self):
        visibles = len(self.tabla._filas)
        total = len(self.filas)
        self.lbl_total.configure(text=f"{visibles} de {total} solicitud(es)")


class PanelIncidentesAdmin(PanelBase):
    TITULO = "Incidentes"
    DESCRIPCION = "Consulta las novedades reportadas y sus solicitudes asociadas."

    def construir(self):
        consulta = next(
            item for item in op.CONSULTAS
            if item["titulo"] == "Incidentes con tipo, cliente y domiciliario")
        self.consulta = consulta
        barra = ttk.Frame(self.contenido, style="Contenido.TFrame")
        barra.pack(fill="x", pady=(0, 10))
        self.lbl_total = ttk.Label(barra, text="", style="Subtitulo.TLabel")
        self.lbl_total.pack(side="right")
        self.ent_busqueda = entrada_busqueda(barra, self._buscar, ancho=250)
        self.ent_busqueda.pack(side="right", padx=10)
        self._btn_actualizar = boton_estilizado(
            barra, "Actualizar", self._recargar, primario=False)
        self._btn_actualizar.pack(side="left")
        self.tabla = TablaDatos(self.contenido, [
            ("codigoIncidente", "Incidente", 90),
            ("Tipo incidente", "Tipo", 150),
            ("numeroSolicitud", "Solicitud", 90),
            ("identificacionCliente", "ID cliente", 110),
            ("identificacionDomiciliario", "ID domiciliario", 125),
        ])
        self.tabla.pack(fill="both", expand=True)
        self._recargar()

    def _recargar(self):
        self._btn_actualizar.configure(state="disabled")
        self.lbl_total.configure(text="Cargando incidentes…")
        ejecutar_en_segundo_plano(
            self, lambda: op.ejecutar_guardada(self.consulta),
            self._cargar, self._fallo)

    def _cargar(self, filas):
        self._btn_actualizar.configure(state="normal")
        self.tabla.cargar(filas)
        self.tabla.filtrar(self.ent_busqueda.get())
        self._actualizar_total()

    def _fallo(self, error):
        self._btn_actualizar.configure(state="normal")
        self.lbl_total.configure(text="No se pudieron cargar los incidentes")
        messagebox.showerror("Error al cargar incidentes", str(error))

    def _buscar(self, texto):
        self.tabla.filtrar(texto)
        self._actualizar_total()

    def _actualizar_total(self):
        self.lbl_total.configure(
            text=f"{len(self.tabla._filas)} de "
                 f"{len(self.tabla._todas_las_filas)} incidente(s)")


class PanelListaAdmin(PanelBase):
    """Base de listados de consulta para el administrador."""
    COLUMNAS = []

    def construir(self):
        barra = ttk.Frame(self.contenido, style="Contenido.TFrame")
        barra.pack(fill="x", pady=(0, 10))
        self._btn_actualizar = boton_estilizado(
            barra, "Actualizar", self._recargar, primario=False)
        self._btn_actualizar.pack(side="left")
        self.lbl_total = ttk.Label(barra, text="", style="Subtitulo.TLabel")
        self.lbl_total.pack(side="right")
        self.ent_busqueda = entrada_busqueda(barra, self._buscar, ancho=250)
        self.ent_busqueda.pack(side="right", padx=10)
        self.tabla = TablaDatos(self.contenido, self.COLUMNAS)
        self.tabla.pack(fill="both", expand=True)
        self._recargar()

    def obtener_filas(self):
        raise NotImplementedError

    def _recargar(self):
        self._btn_actualizar.configure(state="disabled")
        self.lbl_total.configure(text="Actualizando…")
        ejecutar_en_segundo_plano(
            self, self.obtener_filas, self._cargar, self._fallo)

    def _cargar(self, filas):
        self._btn_actualizar.configure(state="normal")
        self.tabla.cargar(filas)
        self.tabla.filtrar(self.ent_busqueda.get())
        self.lbl_total.configure(
            text=f"{len(self.tabla._filas)} de {len(self.tabla._todas_las_filas)}")

    def _buscar(self, texto):
        self.tabla.filtrar(texto)
        self.lbl_total.configure(
            text=f"{len(self.tabla._filas)} de {len(self.tabla._todas_las_filas)}")

    def _fallo(self, error):
        self._btn_actualizar.configure(state="normal")
        self.lbl_total.configure(text="No se pudieron cargar los datos")
        messagebox.showerror("Error de base de datos", str(error))


class PanelUsuariosAdmin(PanelListaAdmin):
    TITULO = "Usuarios"
    DESCRIPCION = "Consulta los clientes y domiciliarios registrados."
    COLUMNAS = [
        ("identificacion", "Identificación", 130),
        ("nombre", "Nombre", 150),
        ("apellidoPaterno", "Apellido", 150),
        ("tipoUsuario", "Rol", 180),
    ]

    def obtener_filas(self):
        consulta = next(
            item for item in op.CONSULTAS
            if item["titulo"] == "Rol de cada usuario")
        return op.ejecutar_guardada(consulta)


class PanelEstablecimientosAdmin(PanelListaAdmin):
    TITULO = "Establecimientos"
    DESCRIPCION = "Consulta los establecimientos y su categoría."
    COLUMNAS = [
        ("codigoEstablecimiento", "Código", 110),
        ("nombre", "Establecimiento", 250),
        ("tipo", "Categoría", 190),
    ]

    def obtener_filas(self):
        return op_cliente.listar_establecimientos()


class PanelBarriosAdmin(PanelBase):
    TITULO = "Barrios"
    DESCRIPCION = "Agrega barrios con cobertura para que aparezcan en las solicitudes."

    COLUMNAS = [
        ("idBarrio", "ID", 60),
        ("nombreBarrio", "Barrio", 260),
        ("nombreComuna", "Comuna", 220),
    ]

    def construir(self):
        try:
            comunas = op.listar_comunas()
        except ErrorBD as e:
            mostrar_error(self.contenido, e)
            return

        self.comunas = {
            f"{fila['nombreComuna']} (ID {fila['idComuna']})": fila["idComuna"]
            for fila in comunas
        }

        tarjeta = ttk.Frame(self.contenido, style="Tarjeta.TFrame", padding=18)
        tarjeta.pack(fill="x", pady=(0, 12))
        ttk.Label(tarjeta, text="Nuevo barrio", style="TarjetaTitulo.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(tarjeta, text="Nombre del barrio", style="Campo.TLabel").grid(
            row=1, column=0, sticky="w", padx=(0, 18), pady=(10, 0))
        ttk.Label(tarjeta, text="Comuna", style="Campo.TLabel").grid(
            row=1, column=1, sticky="w", pady=(10, 0))

        self.ent_nombre = entrada_estilizada(
            tarjeta, ancho=280, placeholder="Nombre del barrio")
        self.ent_nombre.grid(row=2, column=0, sticky="w", padx=(0, 18), pady=(3, 0))
        limitar_campo(self.ent_nombre, MAX_TEXTO_SQL)

        self.cmb_comuna = combo_estilizado(
            tarjeta, list(self.comunas), ancho=300)
        self.cmb_comuna.grid(row=2, column=1, sticky="w", pady=(3, 0))
        boton_estilizado(tarjeta, "Agregar barrio", self._agregar).grid(
            row=2, column=2, padx=(18, 0), pady=(3, 0))

        self.tabla = TablaDatos(self.contenido, self.COLUMNAS)
        self.tabla.pack(fill="both", expand=True)
        self._recargar()

    def _recargar(self):
        try:
            self.tabla.cargar(op.listar_barrios())
        except ErrorBD as e:
            messagebox.showerror("Error de base de datos", str(e))

    def _agregar(self):
        nombre = self.ent_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Revisa el formulario", "Escribe el nombre del barrio.")
            return
        if not self.cmb_comuna.get():
            messagebox.showwarning("Revisa el formulario", "Selecciona una comuna.")
            return
        try:
            op.crear_barrio(nombre, self.comunas[self.cmb_comuna.get()])
        except (ErrorBD, ValueError) as e:
            messagebox.showerror("No se pudo agregar el barrio", str(e))
            return

        self.ent_nombre.delete(0, "end")
        self.cmb_comuna.set("")
        self._recargar()
        messagebox.showinfo("Barrio agregado", f"«{nombre}» ya tiene cobertura.")


class PanelConsultas(PanelBase):
    TITULO = "Consultas"
    DESCRIPCION = "Consultas SQL del proyecto: elige una y ejecútala."

    def construir(self):
        self.por_titulo = {c["titulo"]: c for c in op.CONSULTAS}

        barra = ttk.Frame(self.contenido, style="Contenido.TFrame")
        barra.pack(fill="x")
        self.cmb = combo_estilizado(
            barra, list(self.por_titulo), ancho=500,
            comando=self._seleccionar)
        self.cmb.pack(side="left")
        boton_estilizado(barra, "Ejecutar", self._ejecutar).pack(
            side="left", padx=8)

        

        self.zona = ttk.Frame(self.contenido, style="Contenido.TFrame")
        self.zona.pack(fill="both", expand=True, pady=(10, 0))

    def _seleccionar(self, _evento=None):
        consulta = self.por_titulo[self.cmb.get()]
        self.lbl_tecnica.configure(text=f"Técnica: {consulta['tecnica']}")
        self.txt_sql.configure(state="normal")
        self.txt_sql.delete("1.0", "end")
        self.txt_sql.insert("1.0", consulta["sql"])
        self.txt_sql.configure(state="disabled")

    def _ejecutar(self):
        if not self.cmb.get():
            messagebox.showinfo("Elige una consulta", "Selecciona una consulta de la lista.")
            return
        consulta = self.por_titulo[self.cmb.get()]
        try:
            filas = op.ejecutar_guardada(consulta)
        except ErrorBD as e:
            messagebox.showerror("Error al ejecutar la consulta", str(e))
            return

        for hijo in self.zona.winfo_children():
            hijo.destroy()
        if not filas:
            ttk.Label(self.zona, text="La consulta no devolvió filas.",
                      style="Subtitulo.TLabel").pack(anchor="w")
            return
        tabla = TablaDatos(self.zona, [(k, k, 140) for k in filas[0].keys()], alto=10)
        tabla.pack(fill="both", expand=True)
        tabla.cargar(filas)
