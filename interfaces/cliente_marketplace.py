"""Creación de solicitudes mediante un flujo guiado paso a paso."""
from decimal import Decimal, InvalidOperation
from io import BytesIO
from threading import Thread
import tkinter as tk
from tkinter import ttk, messagebox
from urllib.request import urlopen

from database.conexion import ErrorBD
from interfaces.componentes import limitar_campo, mostrar_error
from interfaces.estilos import COLORES
from interfaces.panel_base import PanelBase
from interfaces.validaciones import MAX_TEXTO_SQL
from operaciones import cliente as op
from operaciones.accesos import listar_barrios
from operaciones.catalogos import catalogo_para_establecimiento

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None


ICONOS_CATEGORIA = {
    "Farmacia": "💊",
    "Restaurante": "🍽️",
    "Supermercado": "🛒",
    "Tienda especializada": "🛍️",
}


class PanelNuevaSolicitudMarketplace(PanelBase):
    """Asistente para crear una solicitud con un solo producto."""

    TITULO = "Crear solicitud"
    DESCRIPCION = "Completa los pasos para registrar tu solicitud."

    def construir(self):
        try:
            self.metodos = {
                fila["nombreMetodoPago"]: fila["idMetodoPago"]
                for fila in op.listar_metodos_pago()
            }
            self.tipos = {
                fila["nombreTipoRecogida"]: fila["idTipoRecogida"]
                for fila in op.listar_tipos_recogida()
            }
            self.establecimientos = {
                fila["nombre"]: {
                    "codigo": fila["codigoEstablecimiento"],
                    "tipo": fila.get("tipo", "Establecimiento"),
                }
                for fila in op.listar_establecimientos()
            }
            self.barrios = {
                fila["nombreBarrio"]: fila["idBarrio"]
                for fila in listar_barrios()
            }
        except ErrorBD as error:
            mostrar_error(self.contenido, error)
            return

        self.tipo_actual = None
        self.categoria_actual = None
        self.establecimiento_actual = None
        self.producto_actual = None
        self.datos_externos = {}
        self.imagenes_cache = {}
        self.canvas_rueda = None
        self.indice_paso = 0
        self.pasos = []

        self._construir_asistente()
        self._configurar_pasos()
        self._mostrar_paso()

    def _construir_asistente(self):
        self.marco_asistente = ttk.Frame(
            self.contenido, style="Tarjeta.TFrame", padding=22)
        self.marco_asistente.pack(fill="both", expand=True)

        self.marco_progreso = ttk.Frame(
            self.marco_asistente, style="Tarjeta.TFrame")
        self.marco_progreso.pack(fill="x", pady=(0, 18))
        self.indicadores = ttk.Frame(
            self.marco_progreso, style="Tarjeta.TFrame")
        self.indicadores.pack(fill="x")

        self.lbl_paso = ttk.Label(
            self.marco_asistente, text="", style="TarjetaTitulo.TLabel")
        self.lbl_paso.pack(anchor="w")
        self.lbl_ayuda = ttk.Label(
            self.marco_asistente, text="", style="TarjetaTexto.TLabel",
            wraplength=760)
        self.lbl_ayuda.pack(anchor="w", pady=(3, 14))

        self.contenido_paso = ttk.Frame(
            self.marco_asistente, style="Tarjeta.TFrame")
        self.contenido_paso.pack(fill="both", expand=True)

        self.marco_navegacion = ttk.Frame(
            self.marco_asistente, style="Tarjeta.TFrame")
        self.marco_navegacion.pack(fill="x", pady=(18, 0))
        self.btn_atras = ttk.Button(
            self.marco_navegacion, text="← Atrás",
            style="Secundario.TButton", command=self._paso_anterior)
        self.btn_atras.pack(side="left")
        self.btn_continuar = ttk.Button(
            self.marco_navegacion, text="Continuar →",
            style="Accion.TButton", command=self._paso_siguiente)
        self.btn_continuar.pack(side="right")

    def _configurar_pasos(self):
        self.pasos = [("tipo", "Tipo de recogida")]
        if self.tipo_actual and self.tipo_actual.casefold() == "externa":
            self.pasos += [
                ("externa", "Datos de recogida"),
                ("confirmar", "Confirmar"),
            ]
        else:
            self.pasos += [
                ("categoria", "Categoría"),
                ("establecimiento", "Establecimiento"),
                ("producto", "Producto"),
                ("confirmar", "Confirmar"),
            ]
        if self.indice_paso >= len(self.pasos):
            self.indice_paso = len(self.pasos) - 1

    def _mostrar_progreso(self):
        for hijo in self.indicadores.winfo_children():
            hijo.destroy()
        for indice, (_, titulo) in enumerate(self.pasos):
            activo = indice == self.indice_paso
            terminado = indice < self.indice_paso
            estilo = "MenuActivo.TButton" if activo else "Secundario.TButton"
            texto = f"✓ {titulo}" if terminado else f"{indice + 1}. {titulo}"
            ttk.Label(
                self.indicadores, text=texto,
                style="TarjetaTitulo.TLabel" if activo else "TarjetaTexto.TLabel"
            ).pack(side="left", padx=(0, 22))

    def _limpiar_contenido_paso(self):
        for hijo in self.contenido_paso.winfo_children():
            hijo.destroy()
        self.canvas_rueda = None

    def _mostrar_paso(self):
        self._configurar_pasos()
        self._mostrar_progreso()
        self._limpiar_contenido_paso()
        clave = self.pasos[self.indice_paso][0]

        if clave == "tipo":
            self._mostrar_tipo()
        elif clave == "categoria":
            self._mostrar_categoria()
        elif clave == "establecimiento":
            self._mostrar_establecimientos()
        elif clave == "producto":
            self._mostrar_productos()
        elif clave == "externa":
            self._mostrar_recogida_externa()
        else:
            self._mostrar_confirmacion()

        self.btn_atras.configure(
            state="normal" if self.indice_paso > 0 else "disabled")
        if clave == "confirmar":
            self.btn_continuar.configure(
                text="Enviar solicitud", command=self._crear)
        else:
            self.btn_continuar.configure(
                text="Continuar →", command=self._paso_siguiente)

    def _mostrar_tipo(self):
        self.lbl_paso.configure(text="1. ¿Cómo quieres realizar la solicitud?")
        self.lbl_ayuda.configure(
            text="Selecciona si la solicitud está relacionada con un establecimiento "
                 "o con una dirección externa.")

        marco = ttk.Frame(self.contenido_paso, style="Tarjeta.TFrame")
        marco.pack(expand=True, fill="both", padx=8, pady=8)
        marco.columnconfigure(0, weight=1)
        marco.columnconfigure(1, weight=1)

        tipos = list(self.tipos)
        for indice, tipo in enumerate(tipos):
            seleccionado = self.tipo_actual == tipo
            titulo = "Establecimiento" if tipo.casefold() == "establecimiento" else "Recogida externa"
            descripcion = (
                "Elige un establecimiento y un producto del catálogo."
                if tipo.casefold() == "establecimiento"
                else "Indica qué se debe recoger y completa la dirección."
            )
            tarjeta = ttk.Frame(
                marco, style="Menu.TFrame" if seleccionado else "Tarjeta.TFrame",
                padding=18)
            tarjeta.grid(
                row=0, column=indice, padx=10, pady=18,
                sticky="nsew")
            ttk.Label(
                tarjeta, text="🏪" if tipo.casefold() == "establecimiento" else "📍",
                style="TarjetaTitulo.TLabel", font=("Segoe UI", 24, "bold")
            ).pack(anchor="w")
            ttk.Label(
                tarjeta, text=titulo, style="TarjetaTitulo.TLabel"
            ).pack(anchor="w", pady=(8, 3))
            ttk.Label(
                tarjeta, text=descripcion, style="TarjetaTexto.TLabel",
                wraplength=260, justify="left"
            ).pack(anchor="w", fill="x", expand=True)
            ttk.Button(
                tarjeta,
                text="Seleccionado" if seleccionado else "Seleccionar",
                style="MenuActivo.TButton" if seleccionado else "Secundario.TButton",
                command=lambda valor=tipo: self._seleccionar_tipo(valor)
            ).pack(anchor="w", pady=(16, 0))

    def _seleccionar_tipo(self, tipo):
        cambio = self.tipo_actual and self.tipo_actual != tipo
        self.tipo_actual = tipo
        if cambio:
            self.categoria_actual = None
            self.establecimiento_actual = None
            self.producto_actual = None
            self.datos_externos = {}
            self.indice_paso = 0
        self._configurar_pasos()
        self._mostrar_paso()

    def _categorias(self):
        return sorted({
            datos["tipo"] for datos in self.establecimientos.values()
            if datos.get("tipo")
        })

    def _mostrar_categoria(self):
        self.lbl_paso.configure(text="2. Elige una categoría")
        self.lbl_ayuda.configure(
            text="Selecciona una categoría para mostrar los establecimientos disponibles.")
        self._crear_zona_desplazable(self._dibujar_categorias)

    def _dibujar_categorias(self, interior, _canvas):
        for indice, categoria in enumerate(self._categorias()):
            seleccionado = self.categoria_actual == categoria
            tarjeta = ttk.Frame(
                interior,
                style="Menu.TFrame" if seleccionado else "Tarjeta.TFrame",
                padding=18)
            tarjeta.grid(
                row=indice // 3, column=indice % 3,
                padx=8, pady=8, sticky="nsew")
            interior.columnconfigure(indice % 3, weight=1)
            ttk.Label(
                tarjeta, text=ICONOS_CATEGORIA.get(categoria, "📦"),
                style="TarjetaTitulo.TLabel", font=("Segoe UI", 24, "bold")
            ).pack(anchor="w")
            ttk.Label(
                tarjeta, text=categoria, style="TarjetaTitulo.TLabel"
            ).pack(anchor="w", pady=(8, 3))
            cantidad = sum(
                1 for datos in self.establecimientos.values()
                if datos.get("tipo") == categoria)
            ttk.Label(
                tarjeta, text=f"{cantidad} establecimiento(s)",
                style="TarjetaTexto.TLabel"
            ).pack(anchor="w")
            ttk.Button(
                tarjeta,
                text="Seleccionada" if seleccionado else "Elegir categoría",
                style="MenuActivo.TButton" if seleccionado else "Secundario.TButton",
                command=lambda valor=categoria: self._seleccionar_categoria(valor)
            ).pack(anchor="w", pady=(14, 0))
            self._registrar_rueda_recursivo(tarjeta, _canvas)

    def _seleccionar_categoria(self, categoria):
        self.categoria_actual = categoria
        self.establecimiento_actual = None
        self.producto_actual = None
        self._mostrar_paso()

    def _establecimientos_de_categoria(self):
        return [
            (nombre, datos)
            for nombre, datos in self.establecimientos.items()
            if datos.get("tipo") == self.categoria_actual
        ]

    def _mostrar_establecimientos(self):
        self.lbl_paso.configure(text="3. Elige un establecimiento")
        self.lbl_ayuda.configure(
            text=f"Selecciona dónde se encuentra tu producto de {self.categoria_actual}.")
        self._crear_zona_desplazable(self._dibujar_establecimientos)

    def _dibujar_establecimientos(self, interior, _canvas):
        establecimientos = self._establecimientos_de_categoria()
        if not establecimientos:
            ttk.Label(
                interior, text="No hay establecimientos disponibles para esta categoría.",
                style="TarjetaTexto.TLabel").pack(anchor="w", padx=12, pady=12)
            return

        for indice, (nombre, datos) in enumerate(establecimientos):
            seleccionado = self.establecimiento_actual == nombre
            tarjeta = ttk.Frame(
                interior,
                style="Menu.TFrame" if seleccionado else "Tarjeta.TFrame",
                padding=16)
            tarjeta.grid(
                row=indice // 2, column=indice % 2,
                padx=8, pady=8, sticky="nsew")
            interior.columnconfigure(indice % 2, weight=1)
            ttk.Label(
                tarjeta, text=nombre, style="TarjetaTitulo.TLabel",
                wraplength=280, justify="left"
            ).pack(anchor="w")
            ttk.Label(
                tarjeta, text=datos["tipo"], style="TarjetaTexto.TLabel"
            ).pack(anchor="w", pady=(4, 0))
            productos = catalogo_para_establecimiento(nombre)
            ttk.Label(
                tarjeta, text=f"{len(productos)} producto(s) disponibles",
                style="TarjetaTexto.TLabel"
            ).pack(anchor="w", pady=(2, 0))
            ttk.Button(
                tarjeta,
                text="Seleccionado" if seleccionado else "Elegir establecimiento",
                style="MenuActivo.TButton" if seleccionado else "Accion.TButton",
                command=lambda valor=nombre: self._seleccionar_establecimiento(valor)
            ).pack(anchor="w", pady=(13, 0))
            self._registrar_rueda_recursivo(tarjeta, _canvas)

    def _seleccionar_establecimiento(self, nombre):
        self.establecimiento_actual = nombre
        self.producto_actual = None
        self._mostrar_paso()

    def _mostrar_productos(self):
        self.lbl_paso.configure(text="4. Elige un producto")
        self.lbl_ayuda.configure(
            text=f"Selecciona un solo producto de {self.establecimiento_actual}. "
                 "Puedes buscarlo por nombre.")

        barra = ttk.Frame(self.contenido_paso, style="Tarjeta.TFrame")
        barra.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Label(
            barra, text="Buscar producto", style="Campo.TLabel"
        ).pack(side="left", padx=(0, 8))
        self.ent_busqueda_producto = ttk.Entry(barra, width=34)
        self.ent_busqueda_producto.pack(side="left", fill="x", expand=True)
        limitar_campo(self.ent_busqueda_producto, MAX_TEXTO_SQL)
        self.ent_busqueda_producto.bind(
            "<KeyRelease>", lambda _evento: self._actualizar_lista_productos())

        self.marco_lista_productos = ttk.Frame(
            self.contenido_paso, style="Tarjeta.TFrame")
        self.marco_lista_productos.pack(fill="both", expand=True)
        self._crear_zona_desplazable(
            self._dibujar_productos, self.marco_lista_productos)

    def _actualizar_lista_productos(self):
        for hijo in self.marco_lista_productos.winfo_children():
            hijo.destroy()
        self._crear_zona_desplazable(
            self._dibujar_productos, self.marco_lista_productos)

    def _dibujar_productos(self, interior, _canvas):
        buscado = " ".join(
            self.ent_busqueda_producto.get().strip().casefold().split())
        productos = catalogo_para_establecimiento(self.establecimiento_actual)
        if buscado:
            productos = [
                producto for producto in productos
                if buscado in producto["nombre"].casefold()
            ]

        if not productos:
            ttk.Label(
                interior, text="No encontramos productos con esa búsqueda.",
                style="TarjetaTexto.TLabel").pack(anchor="w", padx=12, pady=12)
            return

        for indice, producto in enumerate(productos):
            tarjeta = self._crear_tarjeta_producto(interior, producto, _canvas)
            tarjeta.grid(
                row=indice // 3, column=indice % 3,
                padx=7, pady=7, sticky="nsew")
            interior.columnconfigure(indice % 3, weight=1)

    def _crear_tarjeta_producto(self, padre, producto, canvas):
        seleccionado = (
            self.producto_actual is not None
            and self.producto_actual["nombre"] == producto["nombre"])
        tarjeta = ttk.Frame(
            padre,
            style="Menu.TFrame" if seleccionado else "Tarjeta.TFrame",
            padding=9, width=210, height=230)
        tarjeta.grid_propagate(False)

        imagen = ttk.Label(
            tarjeta, text="Cargando imagen...",
            style="TarjetaTexto.TLabel", anchor="center")
        imagen.pack(fill="both", expand=True)
        self._cargar_imagen(imagen, producto.get("imagen"))
        ttk.Label(
            tarjeta, text=producto["nombre"], style="TarjetaTitulo.TLabel",
            wraplength=190, justify="left"
        ).pack(anchor="w", pady=(6, 0))
        ttk.Label(
            tarjeta, text=f"${producto['precio']:,.0f}",
            style="TarjetaTitulo.TLabel"
        ).pack(anchor="w", pady=(3, 0))
        ttk.Button(
            tarjeta,
            text="Producto seleccionado" if seleccionado else "Seleccionar producto",
            style="MenuActivo.TButton" if seleccionado else "Accion.TButton",
            command=lambda item=producto: self._seleccionar_producto(item)
        ).pack(fill="x", pady=(7, 0))
        self._registrar_rueda_recursivo(tarjeta, canvas)
        return tarjeta

    def _seleccionar_producto(self, producto):
        self.producto_actual = producto
        self._mostrar_paso()

    def _crear_zona_desplazable(self, dibujar, padre=None):
        padre = padre or self.contenido_paso
        zona = ttk.Frame(padre, style="Tarjeta.TFrame")
        zona.pack(fill="both", expand=True, padx=8, pady=4)
        canvas = tk.Canvas(
            zona, background=COLORES["tarjeta"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            zona, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        interior = ttk.Frame(canvas, style="Tarjeta.TFrame")
        ventana = canvas.create_window((0, 0), window=interior, anchor="nw")
        interior.bind(
            "<Configure>",
            lambda _evento: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind(
            "<Configure>",
            lambda evento: canvas.itemconfigure(ventana, width=evento.width))
        self.canvas_rueda = canvas
        self._registrar_rueda_recursivo(canvas, canvas)
        dibujar(interior, canvas)
        self._registrar_rueda_recursivo(interior, canvas)

    def _registrar_rueda_recursivo(self, widget, canvas):
        widget.bind(
            "<Enter>", lambda _evento, c=canvas: self._activar_rueda(c), add="+")
        widget.bind(
            "<Leave>", lambda _evento, c=canvas: self._desactivar_rueda(c), add="+")
        widget.bind(
            "<MouseWheel>",
            lambda evento, c=canvas: self._mover_rueda(evento, c), add="+")
        widget.bind(
            "<Button-4>",
            lambda evento, c=canvas: self._mover_rueda_linux(evento, c, -1), add="+")
        widget.bind(
            "<Button-5>",
            lambda evento, c=canvas: self._mover_rueda_linux(evento, c, 1), add="+")
        for hijo in widget.winfo_children():
            self._registrar_rueda_recursivo(hijo, canvas)

    def _activar_rueda(self, canvas):
        self.canvas_rueda = canvas

    def _desactivar_rueda(self, canvas):
        if self.canvas_rueda == canvas:
            self.canvas_rueda = None

    def _mover_rueda(self, evento, canvas):
        self._activar_rueda(canvas)
        unidades = -int(evento.delta / 120)
        if unidades == 0:
            unidades = -1 if evento.delta > 0 else 1
        canvas.yview_scroll(unidades, "units")
        return "break"

    def _mover_rueda_linux(self, _evento, canvas, direccion):
        canvas.yview_scroll(direccion, "units")
        return "break"

    def _mostrar_recogida_externa(self):
        self.lbl_paso.configure(text="2. Datos de recogida externa")
        self.lbl_ayuda.configure(
            text="Describe qué se debe recoger, indica el monto y completa la dirección.")

        marco = ttk.Frame(self.contenido_paso, style="Tarjeta.TFrame", padding=8)
        marco.pack(fill="x", padx=8, pady=8)
        marco.columnconfigure(0, weight=1)
        marco.columnconfigure(1, weight=1)

        self.ent_desc_externa = ttk.Entry(marco)
        self.ent_monto_externa = ttk.Entry(marco)
        self.ent_via = ttk.Entry(marco)
        self.ent_num = ttk.Entry(marco)
        self.cmb_barrio = ttk.Combobox(
            marco, values=list(self.barrios), state="readonly")

        self._campo(marco, "Descripción", self.ent_desc_externa, 0, 0)
        self._campo(marco, "Monto total ($)", self.ent_monto_externa, 0, 1)
        self._campo(marco, "Vía principal", self.ent_via, 2, 0)
        self._campo(marco, "Número", self.ent_num, 2, 1)
        self._campo(marco, "Barrio", self.cmb_barrio, 4, 0)
        ttk.Label(
            marco,
            text="Si tu barrio no aparece, todavía no tenemos cobertura allí.",
            style="TarjetaTexto.TLabel", wraplength=330
        ).grid(row=6, column=0, columnspan=2, sticky="w", pady=(3, 0))

        limitar_campo(self.ent_desc_externa, MAX_TEXTO_SQL)
        limitar_campo(self.ent_monto_externa, 13)
        limitar_campo(self.ent_via, MAX_TEXTO_SQL)
        limitar_campo(self.ent_num, MAX_TEXTO_SQL)
        if self.datos_externos:
            self.ent_desc_externa.insert(0, self.datos_externos["descripcion"])
            self.ent_monto_externa.insert(0, self.datos_externos["monto"])
            self.ent_via.insert(0, self.datos_externos["via"])
            self.ent_num.insert(0, self.datos_externos["numero"])
            self.cmb_barrio.set(self.datos_externos["barrio"])

    def _campo(self, padre, titulo, widget, fila, columna):
        ttk.Label(
            padre, text=titulo, style="Campo.TLabel"
        ).grid(row=fila, column=columna, sticky="w", padx=8, pady=(8, 2))
        widget.grid(
            row=fila + 1, column=columna, sticky="ew",
            padx=8, pady=(0, 5))

    def _validar_externa(self):
        descripcion = self.ent_desc_externa.get().strip()
        if not descripcion:
            raise ValueError("La descripción es obligatoria.")
        if len(descripcion) > MAX_TEXTO_SQL:
            raise ValueError(
                f"La descripción admite máximo {MAX_TEXTO_SQL} caracteres.")
        try:
            monto = Decimal(
                self.ent_monto_externa.get().strip().replace(",", "."))
        except InvalidOperation:
            raise ValueError("El monto debe ser un número.")
        if monto <= 0:
            raise ValueError("El monto debe ser mayor que cero.")
        if not self.ent_via.get().strip() or not self.ent_num.get().strip():
            raise ValueError("Completa la vía principal y el número.")
        if not self.cmb_barrio.get():
            raise ValueError("Selecciona el barrio de recogida.")
        return descripcion, monto

    def _paso_siguiente(self):
        clave = self.pasos[self.indice_paso][0]
        if clave == "tipo" and not self.tipo_actual:
            messagebox.showwarning(
                "Tipo de recogida", "Selecciona un tipo de recogida para continuar.")
            return
        if clave == "categoria" and not self.categoria_actual:
            messagebox.showwarning(
                "Categoría", "Selecciona una categoría para continuar.")
            return
        if clave == "establecimiento" and not self.establecimiento_actual:
            messagebox.showwarning(
                "Establecimiento", "Selecciona un establecimiento para continuar.")
            return
        if clave == "producto" and not self.producto_actual:
            messagebox.showwarning(
                "Producto", "Selecciona un producto para continuar.")
            return
        if clave == "externa":
            try:
                descripcion, monto = self._validar_externa()
            except ValueError as error:
                messagebox.showwarning("Revisa los datos", str(error))
                return
            self.datos_externos = {
                "descripcion": descripcion,
                "monto": f"{monto:.2f}",
                "via": self.ent_via.get().strip(),
                "numero": self.ent_num.get().strip(),
                "barrio": self.cmb_barrio.get(),
            }

        if self.indice_paso < len(self.pasos) - 1:
            self.indice_paso += 1
            self._mostrar_paso()

    def _paso_anterior(self):
        if self.indice_paso <= 0:
            return
        self.indice_paso -= 1
        self._mostrar_paso()

    def _mostrar_confirmacion(self):
        self.lbl_paso.configure(text=f"{len(self.pasos)}. Revisa y envía tu solicitud")
        self.lbl_ayuda.configure(
            text="Verifica la información antes de enviarla.")

        marco = ttk.Frame(self.contenido_paso, style="Tarjeta.TFrame", padding=16)
        marco.pack(fill="x", padx=8, pady=8)
        marco.columnconfigure(1, weight=1)

        tipo_externo = self.tipo_actual.casefold() == "externa"
        datos_resumen = []
        if tipo_externo:
            descripcion = self.datos_externos["descripcion"]
            monto = Decimal(self.datos_externos["monto"])
            datos_resumen = [
                ("Tipo de recogida", "Recogida externa"),
                ("Descripción", descripcion),
                ("Monto", f"${monto:,.0f}"),
                ("Dirección", f"{self.datos_externos['via']} "
                              f"{self.datos_externos['numero']}"),
                ("Barrio", self.datos_externos["barrio"]),
            ]
        else:
            datos_resumen = [
                ("Tipo de recogida", "Establecimiento"),
                ("Categoría", self.categoria_actual),
                ("Establecimiento", self.establecimiento_actual),
                ("Producto", self.producto_actual["nombre"]),
                ("Total", f"${self.producto_actual['precio']:,.0f}"),
            ]

        for fila, (etiqueta, valor) in enumerate(datos_resumen):
            ttk.Label(
                marco, text=etiqueta, style="Campo.TLabel"
            ).grid(row=fila, column=0, sticky="nw", padx=(0, 22), pady=5)
            ttk.Label(
                marco, text=valor, style="TarjetaTitulo.TLabel",
                wraplength=500, justify="left"
            ).grid(row=fila, column=1, sticky="w", pady=5)

        ttk.Separator(marco).grid(
            row=len(datos_resumen), column=0, columnspan=2,
            sticky="ew", pady=(12, 10))
        ttk.Label(
            marco, text="Método de pago", style="Campo.TLabel"
        ).grid(row=len(datos_resumen) + 1, column=0,
               sticky="w", padx=(0, 22), pady=5)
        self.cmb_metodo = ttk.Combobox(
            marco, values=list(self.metodos), state="readonly", width=30)
        self.cmb_metodo.grid(
            row=len(datos_resumen) + 1, column=1, sticky="w", pady=5)
        if "Efectivo" in self.metodos:
            self.cmb_metodo.set("Efectivo")
        elif self.metodos:
            self.cmb_metodo.current(0)

    def _leer(self):
        if not self.cmb_metodo.get():
            raise ValueError("Selecciona el método de pago.")

        tipo = self.tipo_actual
        datos = {
            "idMetodoPago": self.metodos[self.cmb_metodo.get()],
            "idTipoRecogida": self.tipos[tipo],
            "codigoEstablecimiento": None,
            "via": None,
            "numeroExterno": None,
            "idBarrio": None,
        }
        if tipo.casefold() == "establecimiento":
            if not self.establecimiento_actual or not self.producto_actual:
                raise ValueError("Selecciona un establecimiento y un producto.")
            descripcion = self.producto_actual["nombre"]
            if len(descripcion) > MAX_TEXTO_SQL:
                raise ValueError(
                    f"El nombre del producto supera los {MAX_TEXTO_SQL} caracteres permitidos.")
            datos["descripcion"] = descripcion
            datos["monto"] = Decimal(str(self.producto_actual["precio"]))
            datos["codigoEstablecimiento"] = self.establecimientos[
                self.establecimiento_actual]["codigo"]
            return datos

        if not self.datos_externos:
            raise ValueError("Completa los datos de recogida externa.")
        datos["descripcion"] = self.datos_externos["descripcion"]
        datos["monto"] = Decimal(self.datos_externos["monto"])
        datos["via"] = self.datos_externos["via"]
        datos["numeroExterno"] = self.datos_externos["numero"]
        datos["idBarrio"] = self.barrios[self.datos_externos["barrio"]]
        return datos

    def _crear(self):
        try:
            datos = self._leer()
        except ValueError as error:
            messagebox.showwarning("Revisa el formulario", str(error))
            return
        try:
            numero = op.crear_solicitud(
                self.ventana.sesion["identificacion"], datos)
        except ErrorBD as error:
            messagebox.showerror("No se pudo crear la solicitud", str(error))
            return
        messagebox.showinfo(
            "Solicitud creada",
            f"Tu solicitud quedó registrada con el número {numero}.")
        self.ventana.mostrar_modulo("mis_solicitudes")

    def _cargar_imagen(self, etiqueta, url):
        if not url:
            etiqueta.configure(text="Sin imagen")
            return
        if Image is None or ImageTk is None:
            etiqueta.configure(text="Imagen no disponible")
            return
        if url in self.imagenes_cache:
            etiqueta.configure(image=self.imagenes_cache[url], text="")
            etiqueta.image = self.imagenes_cache[url]
            return

        def descargar():
            try:
                with urlopen(url, timeout=5) as respuesta:
                    imagen = Image.open(
                        BytesIO(respuesta.read())).convert("RGB")
                    imagen.thumbnail((190, 105))
            except Exception:
                imagen = None
            try:
                self.after(
                    0, lambda: self._aplicar_imagen(etiqueta, url, imagen))
            except (RuntimeError, AttributeError):
                pass

        Thread(target=descargar, daemon=True).start()

    def _aplicar_imagen(self, etiqueta, url, imagen):
        try:
            existe = etiqueta.winfo_exists()
        except tk.TclError:
            return
        if not existe:
            return
        if imagen is None:
            etiqueta.configure(text="Imagen no disponible")
            return
        foto = ImageTk.PhotoImage(imagen)
        self.imagenes_cache[url] = foto
        etiqueta.configure(image=foto, text="")
        etiqueta.image = foto
