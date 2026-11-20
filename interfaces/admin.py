"""Módulos del administrador: dashboard, solicitudes y consultas del proyecto."""
import tkinter as tk
from tkinter import ttk, messagebox

from database.conexion import ErrorBD
from interfaces.panel_base import PanelBase
from interfaces.componentes import (
    TablaDatos, GraficoBarras, tarjeta_indicador, mostrar_error)
from operaciones import admin as op


class PanelDashboard(PanelBase):
    TITULO = "Dashboard"
    DESCRIPCION = "Resumen general de la operación."

    def construir(self):
        try:
            estados = op.solicitudes_por_estado()
            conteos = op.conteos_generales()
            efectivo, electronico, total = op.facturacion()
            recientes = op.solicitudes_recientes()
        except ErrorBD as e:
            mostrar_error(self.contenido, e)
            return

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
        rejilla = ttk.Frame(self.contenido, style="Contenido.TFrame")
        rejilla.pack(fill="x")
        for i in range(4):
            rejilla.columnconfigure(i, weight=1, uniform="k")
        for n, (titulo, valor) in enumerate(indicadores):
            tarjeta_indicador(rejilla, titulo, valor).grid(
                row=n // 4, column=n % 4, padx=6, pady=6, sticky="nsew")

        inferior = ttk.Frame(self.contenido, style="Contenido.TFrame")
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
        self.cmb_estado = ttk.Combobox(barra, values=["Todos"] + list(self.estados),
                                       state="readonly", width=18)
        self.cmb_estado.set("Todos")
        self.cmb_estado.pack(side="left", padx=8)
        self.cmb_estado.bind("<<ComboboxSelected>>", lambda e: self._recargar())
        ttk.Button(barra, text="Actualizar", style="Secundario.TButton",
                   command=self._recargar).pack(side="left")
        self.lbl_total = ttk.Label(barra, text="", style="Subtitulo.TLabel")
        self.lbl_total.pack(side="right")

        self.tabla = TablaDatos(self.contenido, self.COLUMNAS)
        self.tabla.pack(fill="both", expand=True)
        self._recargar()

    def _recargar(self):
        id_estado = self.estados.get(self.cmb_estado.get())  # None si es "Todos"
        try:
            filas = op.listar_solicitudes(id_estado)
        except ErrorBD as e:
            messagebox.showerror("Error de base de datos", str(e))
            return
        self.tabla.cargar(filas)
        self.lbl_total.configure(text=f"{len(filas)} solicitud(es)")


class PanelConsultas(PanelBase):
    TITULO = "Consultas"
    DESCRIPCION = "Consultas SQL del proyecto: elige una y ejecútala."

    def construir(self):
        self.por_titulo = {c["titulo"]: c for c in op.CONSULTAS}

        barra = ttk.Frame(self.contenido, style="Contenido.TFrame")
        barra.pack(fill="x")
        self.cmb = ttk.Combobox(barra, values=list(self.por_titulo), state="readonly", width=60)
        self.cmb.pack(side="left")
        self.cmb.bind("<<ComboboxSelected>>", self._seleccionar)
        ttk.Button(barra, text="Ejecutar", style="Accion.TButton",
                   command=self._ejecutar).pack(side="left", padx=8)

        self.lbl_tecnica = ttk.Label(self.contenido, text="", style="Subtitulo.TLabel")
        self.lbl_tecnica.pack(anchor="w", pady=(8, 4))

        self.txt_sql = tk.Text(self.contenido, height=7, font=("Consolas", 9), wrap="none",
                               background="#FFFFFF", relief="solid", borderwidth=1,
                               state="disabled")
        self.txt_sql.pack(fill="x")

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