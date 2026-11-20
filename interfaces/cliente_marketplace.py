"""Creación de solicitudes con una experiencia de catálogo tipo marketplace."""
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


class PanelNuevaSolicitudMarketplace(PanelBase):
    """Catálogo filtrable y carrito que termina en una solicitud existente."""

    TITULO = "Crear solicitud"
    DESCRIPCION = "Busca productos, elige un establecimiento y arma tu solicitud."

    def construir(self):
        try:
            metodos = {
                fila["nombreMetodoPago"]: fila["idMetodoPago"]
                for fila in op.listar_metodos_pago()
            }
            tipos = {
                fila["nombreTipoRecogida"]: fila["idTipoRecogida"]
                for fila in op.listar_tipos_recogida()
            }
            establecimientos = {
                fila["nombre"]: {
                    "codigo": fila["codigoEstablecimiento"],
                    "tipo": fila.get("tipo", "Establecimiento"),
                }
                for fila in op.listar_establecimientos()
            }
            barrios = {
                fila["nombreBarrio"]: fila["idBarrio"]
                for fila in listar_barrios()
            }
        except ErrorBD as error:
            mostrar_error(self.contenido, error)
            return

        self.metodos = metodos
        self.tipos = tipos
        self.establecimientos = establecimientos
        self.barrios = barrios
        self.categoria_actual = "Todos"
        self.establecimiento_actual = None
        self.establecimiento_pedido = None
        self.productos_actuales = []
        self.carrito = []
        self.imagenes_cache = {}

        self._construir_busqueda()
        cuerpo = ttk.Frame(self.contenido, style="Contenido.TFrame")
        cuerpo.pack(fill="both", expand=True)

        self.zona_catalogo = ttk.Frame(cuerpo, style="Contenido.TFrame")
        self.zona_catalogo.pack(
            side="left", fill="both", expand=True, padx=(0, 12))

        self.zona_resumen = ttk.Frame(
            cuerpo, style="Tarjeta.TFrame", padding=16, width=350)
        self.zona_resumen.pack(side="right", fill="y")
        self.zona_resumen.pack_propagate(False)

        self._construir_catalogo()
        self._construir_resumen(metodos, tipos, barrios)
        self._actualizar_catalogo()

    def _construir_busqueda(self):
        barra = ttk.Frame(self.contenido, style="Contenido.TFrame")
        barra.pack(fill="x", pady=(0, 10))
        ttk.Label(
            barra, text="Buscar productos o establecimientos",
            style="Campo.TLabel").pack(side="left", padx=(0, 8))
        self.ent_busqueda = ttk.Entry(barra, width=40)
        self.ent_busqueda.pack(side="left")
        limitar_campo(self.ent_busqueda, MAX_TEXTO_SQL)
        self.ent_busqueda.bind(
            "<KeyRelease>", lambda _evento: self._actualizar_catalogo())

    def _construir_catalogo(self):
        self.marco_explorador = ttk.Frame(
            self.zona_catalogo, style="Contenido.TFrame")
        self.marco_explorador.pack(fill="both", expand=True)

        ttk.Label(
            self.marco_explorador, text="Categorías",
            style="TarjetaTitulo.TLabel").pack(anchor="w")
        self.marco_categorias = ttk.Frame(
            self.marco_explorador, style="Contenido.TFrame")
        self.marco_categorias.pack(fill="x", pady=(6, 10))

        categorias = ["Todos"] + sorted({
            datos["tipo"] for datos in self.establecimientos.values()
            if datos["tipo"]
        })
        for categoria in categorias:
            ttk.Button(
                self.marco_categorias, text=categoria,
                style="MenuActivo.TButton"
                if categoria == "Todos" else "Secundario.TButton",
                command=lambda valor=categoria:
                self._seleccionar_categoria(valor)
            ).pack(side="left", padx=(0, 6))

        ttk.Label(
            self.marco_explorador, text="Establecimientos",
            style="TarjetaTitulo.TLabel").pack(anchor="w")
        contenedor_establecimientos = ttk.Frame(
            self.marco_explorador, style="Contenido.TFrame")
        contenedor_establecimientos.pack(fill="x", pady=(6, 12))
        self.canvas_establecimientos = tk.Canvas(
            contenedor_establecimientos, height=112,
            background=COLORES["fondo"], highlightthickness=0)
        barra_establecimientos = ttk.Scrollbar(
            contenedor_establecimientos, orient="horizontal",
            command=self.canvas_establecimientos.xview)
        self.canvas_establecimientos.configure(
            xscrollcommand=barra_establecimientos.set)
        self.canvas_establecimientos.pack(fill="x")
        barra_establecimientos.pack(fill="x")
        self.inner_establecimientos = ttk.Frame(
            self.canvas_establecimientos, style="Contenido.TFrame")
        self.canvas_establecimientos.create_window(
            (0, 0), window=self.inner_establecimientos, anchor="nw")
        self.inner_establecimientos.bind(
            "<Configure>",
            lambda _evento: self.canvas_establecimientos.configure(
                scrollregion=self.canvas_establecimientos.bbox("all")))

        self.lbl_productos = ttk.Label(
            self.marco_explorador, text="Selecciona un establecimiento",
            style="TarjetaTitulo.TLabel")
        self.lbl_productos.pack(anchor="w", pady=(0, 6))

        contenedor_productos = ttk.Frame(
            self.marco_explorador, style="Contenido.TFrame")
        contenedor_productos.pack(fill="both", expand=True)
        self.canvas_productos = tk.Canvas(
            contenedor_productos, background=COLORES["fondo"],
            highlightthickness=0)
        barra_productos = ttk.Scrollbar(
            contenedor_productos, orient="vertical",
            command=self.canvas_productos.yview)
        self.canvas_productos.configure(yscrollcommand=barra_productos.set)
        self.canvas_productos.pack(side="left", fill="both", expand=True)
        barra_productos.pack(side="right", fill="y")
        self.inner_productos = ttk.Frame(
            self.canvas_productos, style="Contenido.TFrame")
        self.ventana_productos = self.canvas_productos.create_window(
            (0, 0), window=self.inner_productos, anchor="nw")
        self.inner_productos.bind(
            "<Configure>",
            lambda _evento: self.canvas_productos.configure(
                scrollregion=self.canvas_productos.bbox("all")))
        self.canvas_productos.bind(
            "<Configure>",
            lambda evento: self.canvas_productos.itemconfigure(
                self.ventana_productos, width=evento.width))

        self.marco_info_externa = ttk.Frame(
            self.zona_catalogo, style="Tarjeta.TFrame", padding=24)
        ttk.Label(
            self.marco_info_externa, text="Recogida en dirección externa",
            style="TarjetaTitulo.TLabel").pack(anchor="w")
        ttk.Label(
            self.marco_info_externa,
            text="Completa la dirección en «Tu solicitud». "
                 "El catálogo se usa para pedidos de establecimientos.",
            style="TarjetaTexto.TLabel", wraplength=600,
            justify="left").pack(anchor="w", pady=(6, 0))

    def _construir_resumen(self, metodos, tipos, barrios):
        ttk.Label(
            self.zona_resumen, text="Tu solicitud",
            style="TarjetaTitulo.TLabel").pack(anchor="w")
        self.lbl_tienda = ttk.Label(
            self.zona_resumen, text="Selecciona un establecimiento",
            style="TarjetaTexto.TLabel", wraplength=300)
        self.lbl_tienda.pack(anchor="w", pady=(3, 10))

        self.marco_items = ttk.Frame(
            self.zona_resumen, style="Tarjeta.TFrame")
        self.marco_items.pack(fill="x")
        self.lbl_total = ttk.Label(
            self.zona_resumen, text="Total: $0",
            style="TarjetaTitulo.TLabel")
        self.lbl_total.pack(anchor="e", pady=(10, 12))
        ttk.Separator(self.zona_resumen).pack(fill="x", pady=(0, 10))

        ttk.Label(
            self.zona_resumen, text="Tipo de recogida",
            style="Campo.TLabel").pack(anchor="w")
        self.cmb_tipo = ttk.Combobox(
            self.zona_resumen, values=list(tipos),
            state="readonly", width=32)
        self.cmb_tipo.pack(fill="x", pady=(3, 8))
        self.cmb_tipo.bind("<<ComboboxSelected>>", self._cambiar_tipo)

        ttk.Label(
            self.zona_resumen, text="Método de pago",
            style="Campo.TLabel").pack(anchor="w")
        self.cmb_metodo = ttk.Combobox(
            self.zona_resumen, values=list(metodos),
            state="readonly", width=32)
        self.cmb_metodo.pack(fill="x", pady=(3, 8))

        self.marco_externa = ttk.Frame(
            self.zona_resumen, style="Tarjeta.TFrame")
        ttk.Label(
            self.marco_externa, text="Descripción",
            style="Campo.TLabel").pack(anchor="w")
        self.ent_desc_externa = ttk.Entry(self.marco_externa)
        self.ent_desc_externa.pack(fill="x", pady=(3, 6))
        limitar_campo(self.ent_desc_externa, MAX_TEXTO_SQL)

        ttk.Label(
            self.marco_externa, text="Monto total ($)",
            style="Campo.TLabel").pack(anchor="w")
        self.ent_monto_externa = ttk.Entry(self.marco_externa)
        self.ent_monto_externa.pack(fill="x", pady=(3, 6))
        limitar_campo(self.ent_monto_externa, 13)

        ttk.Label(
            self.marco_externa, text="Vía principal",
            style="Campo.TLabel").pack(anchor="w")
        self.ent_via = ttk.Entry(self.marco_externa)
        self.ent_via.pack(fill="x", pady=(3, 6))
        limitar_campo(self.ent_via, MAX_TEXTO_SQL)

        ttk.Label(
            self.marco_externa, text="Número",
            style="Campo.TLabel").pack(anchor="w")
        self.ent_num = ttk.Entry(self.marco_externa)
        self.ent_num.pack(fill="x", pady=(3, 6))
        limitar_campo(self.ent_num, MAX_TEXTO_SQL)

        ttk.Label(
            self.marco_externa, text="Barrio",
            style="Campo.TLabel").pack(anchor="w")
        self.cmb_barrio = ttk.Combobox(
            self.marco_externa, values=list(barrios),
            state="readonly", width=32)
        self.cmb_barrio.pack(fill="x", pady=(3, 2))
        ttk.Label(
            self.marco_externa,
            text="Si tu barrio no aparece, todavía no tenemos cobertura allí.",
            style="TarjetaTexto.TLabel", wraplength=300).pack(
                anchor="w", pady=(2, 8))

        self.boton_enviar = ttk.Button(
            self.zona_resumen, text="Enviar solicitud",
            style="Accion.TButton", command=self._crear)
        self.boton_enviar.pack(fill="x", pady=(12, 0))
        self._render_carrito()

        if "Establecimiento" in tipos:
            self.cmb_tipo.set("Establecimiento")
        elif tipos:
            self.cmb_tipo.current(0)
        if "Efectivo" in metodos:
            self.cmb_metodo.set("Efectivo")
        elif metodos:
            self.cmb_metodo.current(0)

    def _seleccionar_categoria(self, categoria):
        self.categoria_actual = categoria
        for boton in self.marco_categorias.winfo_children():
            boton.configure(
                style="MenuActivo.TButton"
                if boton.cget("text") == categoria
                else "Secundario.TButton")
        self._actualizar_catalogo()

    def _texto_busqueda(self):
        return " ".join(
            self.ent_busqueda.get().strip().casefold().split())

    def _establecimiento_visible(self, nombre, datos):
        if (self.categoria_actual != "Todos"
                and datos["tipo"] != self.categoria_actual):
            return False
        buscado = self._texto_busqueda()
        if not buscado:
            return True
        if (buscado in nombre.casefold()
                or buscado in datos["tipo"].casefold()):
            return True
        return any(
            buscado in producto["nombre"].casefold()
            for producto in catalogo_para_establecimiento(nombre))

    def _actualizar_catalogo(self):
        self._render_establecimientos()
        self._render_productos()

    def _render_establecimientos(self):
        for hijo in self.inner_establecimientos.winfo_children():
            hijo.destroy()

        visibles = [
            (nombre, datos)
            for nombre, datos in self.establecimientos.items()
            if self._establecimiento_visible(nombre, datos)
        ]
        if not visibles:
            ttk.Label(
                self.inner_establecimientos,
                text="No encontramos establecimientos con esa búsqueda.",
                style="TarjetaTexto.TLabel").pack(
                anchor="w", padx=8, pady=12)
            return

        for nombre, datos in visibles:
            tarjeta = ttk.Frame(
                self.inner_establecimientos, style="Tarjeta.TFrame",
                width=180, height=92)
            tarjeta.pack(side="left", padx=(0, 8), pady=4)
            tarjeta.pack_propagate(False)
            ttk.Label(
                tarjeta, text=nombre, style="TarjetaTitulo.TLabel",
                wraplength=165, justify="left").pack(
                anchor="w", padx=10, pady=(8, 0))
            ttk.Label(
                tarjeta, text=datos["tipo"], style="TarjetaTexto.TLabel",
                wraplength=165).pack(anchor="w", padx=10)
            ttk.Button(
                tarjeta, text="Ver productos", style="Accion.TButton",
                command=lambda valor=nombre:
                self._seleccionar_establecimiento(valor)
            ).pack(anchor="w", padx=10, pady=(4, 0))

    def _seleccionar_establecimiento(self, nombre):
        if self.carrito and self.establecimiento_pedido != nombre:
            cambiar = messagebox.askyesno(
                "Cambiar establecimiento",
                "Tu solicitud actual tiene productos de otro establecimiento. "
                "¿Deseas vaciarla y comenzar una nueva?")
            if not cambiar:
                return
            self.carrito = []
            self.establecimiento_pedido = None

        self.establecimiento_actual = nombre
        self.productos_actuales = catalogo_para_establecimiento(nombre)
        datos = self.establecimientos[nombre]
        self.lbl_tienda.configure(
            text=f"{nombre}\n{datos['tipo']} · un establecimiento por solicitud")
        self._render_productos()
        self._render_carrito()

    def _render_productos(self):
        for hijo in self.inner_productos.winfo_children():
            hijo.destroy()
        if not self.establecimiento_actual:
            self.lbl_productos.configure(
                text="Selecciona un establecimiento para ver sus productos")
            ttk.Label(
                self.inner_productos,
                text="Aquí aparecerán sus productos, precios e imágenes.",
                style="TarjetaTexto.TLabel").grid(
                row=0, column=0, padx=12, pady=12, sticky="w")
            return

        buscado = self._texto_busqueda()
        productos = self.productos_actuales
        if buscado and buscado not in self.establecimiento_actual.casefold():
            productos = [
                producto for producto in productos
                if buscado in producto["nombre"].casefold()
            ]
        self.lbl_productos.configure(
            text=f"Productos de {self.establecimiento_actual} "
                 f"({len(productos)} disponibles)")
        if not productos:
            ttk.Label(
                self.inner_productos,
                text="No encontramos productos con esa búsqueda.",
                style="TarjetaTexto.TLabel").grid(
                row=0, column=0, padx=12, pady=12, sticky="w")
            return

        for indice, producto in enumerate(productos):
            tarjeta = ttk.Frame(
                self.inner_productos, style="Tarjeta.TFrame",
                width=220, height=260)
            tarjeta.grid(
                row=indice // 3, column=indice % 3,
                padx=5, pady=5, sticky="n")
            tarjeta.grid_propagate(False)
            imagen = ttk.Label(
                tarjeta, text="Cargando imagen...",
                style="TarjetaTexto.TLabel", anchor="center")
            imagen.grid(
                row=0, column=0, columnspan=2,
                sticky="nsew", padx=5, pady=5)
            tarjeta.rowconfigure(0, weight=1)
            tarjeta.columnconfigure(0, weight=1)
            tarjeta.columnconfigure(1, weight=1)
            self._cargar_imagen(imagen, producto.get("imagen"))
            ttk.Label(
                tarjeta, text=producto["nombre"],
                style="TarjetaTitulo.TLabel",
                wraplength=195, justify="left").grid(
                row=1, column=0, columnspan=2,
                sticky="w", padx=8, pady=(2, 0))
            ttk.Label(
                tarjeta, text=f"${producto['precio']:,.0f}",
                style="TarjetaTitulo.TLabel").grid(
                row=2, column=0, sticky="w", padx=8, pady=(3, 0))
            ttk.Label(
                tarjeta,
                text=f"{self.establecimientos[self.establecimiento_actual]['tipo']} · 20 min",
                style="TarjetaTexto.TLabel").grid(
                row=3, column=0, columnspan=2, sticky="w", padx=8)
            ttk.Button(
                tarjeta, text="+ Agregar", style="Accion.TButton",
                command=lambda item=producto:
                self._agregar_producto(item)
            ).grid(
                row=4, column=0, columnspan=2,
                sticky="ew", padx=8, pady=(5, 8))

    def _cargar_imagen(self, etiqueta, url):
        if not url:
            etiqueta.configure(text="Sin imagen")
            return
        if Image is None or ImageTk is None:
            etiqueta.configure(text=url, wraplength=180)
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
                    imagen.thumbnail((200, 120))
            except Exception:
                imagen = None
            try:
                self.after(
                    0, lambda: self._aplicar_imagen(etiqueta, url, imagen))
            except (RuntimeError, AttributeError):
                pass

        Thread(target=descargar, daemon=True).start()

    def _aplicar_imagen(self, etiqueta, url, imagen):
        if not etiqueta.winfo_exists():
            return
        if imagen is None:
            etiqueta.configure(text="Imagen no disponible")
            return
        foto = ImageTk.PhotoImage(imagen)
        self.imagenes_cache[url] = foto
        etiqueta.configure(image=foto, text="")
        etiqueta.image = foto

    def _agregar_producto(self, producto):
        if not self.establecimiento_actual:
            return
        if (self.establecimiento_pedido
                and self.establecimiento_pedido != self.establecimiento_actual):
            messagebox.showwarning(
                "Un solo establecimiento",
                "Una solicitud solo puede contener productos del mismo "
                "establecimiento.")
            return
        if not self.establecimiento_pedido:
            self.establecimiento_pedido = self.establecimiento_actual

        carrito_anterior = [item.copy() for item in self.carrito]
        for item in self.carrito:
            if item["nombre"] == producto["nombre"]:
                item["cantidad"] += 1
                break
        else:
            self.carrito.append({
                "nombre": producto["nombre"],
                "precio": Decimal(str(producto["precio"])),
                "cantidad": 1,
            })
        if len(self._descripcion_solicitud()) > MAX_TEXTO_SQL:
            self.carrito = carrito_anterior
            messagebox.showwarning(
                "Descripción demasiado larga",
                "El SQL permite máximo 50 caracteres para describir "
                "la solicitud. Reduce productos o cantidades.")
            return
        self._render_carrito()

    def _cambiar_cantidad(self, indice, cambio):
        if not 0 <= indice < len(self.carrito):
            return
        self.carrito[indice]["cantidad"] += cambio
        if self.carrito[indice]["cantidad"] <= 0:
            del self.carrito[indice]
        if not self.carrito:
            self.establecimiento_pedido = None
        self._render_carrito()

    def _render_carrito(self):
        for hijo in self.marco_items.winfo_children():
            hijo.destroy()
        if not self.carrito:
            ttk.Label(
                self.marco_items, text="Aún no has agregado productos.",
                style="TarjetaTexto.TLabel").pack(
                anchor="w", padx=8, pady=10)
            self.lbl_total.configure(text="Total: $0")
            return

        for indice, item in enumerate(self.carrito):
            fila = ttk.Frame(self.marco_items, style="Tarjeta.TFrame")
            fila.pack(fill="x", padx=5, pady=3)
            subtotal = item["precio"] * item["cantidad"]
            ttk.Label(
                fila, text=item["nombre"], style="TarjetaTexto.TLabel",
                wraplength=135, justify="left").grid(
                row=0, column=0, rowspan=2,
                sticky="w", padx=6, pady=4)
            ttk.Label(
                fila, text=f"${subtotal:,.0f}",
                style="TarjetaTexto.TLabel").grid(
                row=0, column=1, sticky="e", padx=6, pady=(4, 0))
            ttk.Button(
                fila, text="-", width=2, style="Secundario.TButton",
                command=lambda i=indice: self._cambiar_cantidad(i, -1)
            ).grid(row=1, column=1, sticky="e", padx=(0, 2), pady=(0, 4))
            ttk.Label(
                fila, text=str(item["cantidad"]),
                style="TarjetaTexto.TLabel").grid(
                row=1, column=2, pady=(0, 4))
            ttk.Button(
                fila, text="+", width=2, style="Secundario.TButton",
                command=lambda i=indice: self._cambiar_cantidad(i, 1)
            ).grid(row=1, column=3, padx=(2, 6), pady=(0, 4))
            fila.columnconfigure(0, weight=1)

        self.lbl_total.configure(
            text=f"Total: ${self._total_carrito():,.0f}")

    def _total_carrito(self):
        return sum(
            (item["precio"] * item["cantidad"] for item in self.carrito),
            Decimal("0"))

    def _descripcion_solicitud(self):
        return ", ".join(
            f"{item['nombre']} x{item['cantidad']}"
            for item in self.carrito)

    def _cambiar_tipo(self, _evento=None):
        tipo = self.cmb_tipo.get()
        if tipo.casefold() == "externa":
            if self.carrito:
                cambiar = messagebox.askyesno(
                    "Cambiar tipo de recogida",
                    "La solicitud actual tiene productos. ¿Deseas vaciarla "
                    "para usar una dirección externa?")
                if not cambiar:
                    self.cmb_tipo.set("Establecimiento")
                    return
                self.carrito = []
                self.establecimiento_pedido = None
            self.marco_explorador.pack_forget()
            self.marco_info_externa.pack(fill="both", expand=True)
            self.marco_externa.pack(
                fill="x", pady=(0, 8), before=self.boton_enviar)
            self._render_carrito()
        else:
            self.marco_info_externa.pack_forget()
            self.marco_explorador.pack(fill="both", expand=True)
            self.marco_externa.pack_forget()

    def _leer(self):
        if not self.cmb_metodo.get():
            raise ValueError("Selecciona el método de pago.")
        tipo = self.cmb_tipo.get()
        if not tipo:
            raise ValueError("Selecciona el tipo de recogida.")

        datos = {
            "idMetodoPago": self.metodos[self.cmb_metodo.get()],
            "idTipoRecogida": self.tipos[tipo],
            "codigoEstablecimiento": None,
            "via": None,
            "numeroExterno": None,
            "idBarrio": None,
        }
        if tipo.casefold() == "establecimiento":
            if not self.establecimiento_pedido or not self.carrito:
                raise ValueError(
                    "Selecciona un establecimiento y agrega al menos "
                    "un producto.")
            descripcion = self._descripcion_solicitud()
            if len(descripcion) > MAX_TEXTO_SQL:
                raise ValueError(
                    f"La descripción admite máximo {MAX_TEXTO_SQL} caracteres.")
            datos["descripcion"] = descripcion
            datos["monto"] = self._total_carrito()
            datos["codigoEstablecimiento"] = self.establecimientos[
                self.establecimiento_pedido]["codigo"]
            return datos

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
        via = self.ent_via.get().strip()
        numero = self.ent_num.get().strip()
        if not via or not numero or not self.cmb_barrio.get():
            raise ValueError(
                "Completa la dirección de recogida (vía, número y barrio).")
        datos["descripcion"] = descripcion
        datos["monto"] = monto
        datos["via"] = via
        datos["numeroExterno"] = numero
        datos["idBarrio"] = self.barrios[self.cmb_barrio.get()]
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
