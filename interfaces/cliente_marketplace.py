"""Creación de solicitudes mediante un flujo guiado paso a paso."""
from decimal import Decimal, InvalidOperation
from io import BytesIO
from threading import Thread
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
from urllib.request import urlopen

from database.conexion import ErrorBD
from interfaces.componentes import (
    limitar_campo, mostrar_error, ejecutar_en_segundo_plano)
from interfaces.estilos import COLORES
from interfaces.panel_base import PanelBase
from interfaces.validaciones import MAX_TEXTO_SQL
from operaciones import cliente as op
from operaciones.accesos import listar_barrios
from operaciones.catalogos import catalogo_para_establecimiento

try:
    from PIL import Image, ImageOps, ImageTk
except ImportError:
    Image = ImageOps = ImageTk = None


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
        self.lbl_cargando = ctk.CTkLabel(
            self.contenido, text="Cargando establecimientos y opciones…",
            text_color=COLORES["texto_suave"], font=("Segoe UI", 12))
        self.lbl_cargando.pack(anchor="w", padx=12, pady=12)
        ejecutar_en_segundo_plano(
            self, self._cargar_opciones, self._iniciar_asistente,
            self._fallo_carga)

    @staticmethod
    def _cargar_opciones():
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
        return metodos, tipos, establecimientos, barrios

    def _iniciar_asistente(self, opciones):
        self.lbl_cargando.destroy()
        (self.metodos, self.tipos,
         self.establecimientos, self.barrios) = opciones

        self.tipo_actual = None
        self.categoria_actual = None
        self.establecimiento_actual = None
        self.producto_actual = None
        self.datos_externos = {}
        self.metodo_pago_actual = None
        self.imagenes_cache = {}
        self.canvas_rueda = None
        self.indice_paso = 0
        self.pasos = []

        self._construir_asistente()
        self._configurar_pasos()
        self._mostrar_paso()

    def _fallo_carga(self, error):
        self.lbl_cargando.destroy()
        mostrar_error(self.contenido, error)

    def _construir_asistente(self):
        self.marco_asistente = ctk.CTkFrame(
            self.contenido, fg_color=COLORES["tarjeta"], corner_radius=18,
            border_width=1, border_color=COLORES["borde"])
        self.marco_asistente.pack(fill="both", expand=True, padx=4, pady=4)

        self.marco_progreso = ctk.CTkFrame(
            self.marco_asistente, fg_color="transparent")
        self.marco_progreso.pack(fill="x", padx=22, pady=(20, 14))
        self.indicadores = ctk.CTkFrame(
            self.marco_progreso, fg_color="transparent")
        self.indicadores.pack(fill="x")

        self.lbl_paso = ctk.CTkLabel(
            self.marco_asistente, text="", text_color=COLORES["texto"],
            font=("Segoe UI", 19, "bold"), anchor="w")
        self.lbl_paso.pack(anchor="w", padx=22)
        self.lbl_ayuda = ctk.CTkLabel(
            self.marco_asistente, text="", text_color=COLORES["texto_suave"],
            font=("Segoe UI", 11), wraplength=760, anchor="w", justify="left")
        self.lbl_ayuda.pack(anchor="w", padx=22, pady=(3, 12))

        self.contenido_paso = ctk.CTkFrame(
            self.marco_asistente, fg_color="transparent")
        self.contenido_paso.pack(fill="both", expand=True, padx=14)

        self.marco_navegacion = ctk.CTkFrame(
            self.marco_asistente, fg_color="transparent")
        self.marco_navegacion.pack(fill="x", padx=22, pady=(12, 20))
        self.btn_atras = ctk.CTkButton(
            self.marco_navegacion, text="← Atrás", width=120, height=38,
            corner_radius=9, fg_color=COLORES["tarjeta"],
            hover_color=COLORES["acento_claro"], text_color=COLORES["texto"],
            border_width=1, border_color=COLORES["borde"],
            command=self._paso_anterior)
        self.btn_atras.pack(side="left")
        self.btn_continuar = ctk.CTkButton(
            self.marco_navegacion, text="Continuar →", width=170, height=38,
            corner_radius=9, fg_color=COLORES["acento"],
            hover_color="#E66F10", font=("Segoe UI", 11, "bold"),
            command=self._paso_siguiente)
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
            texto = f"✓ {titulo}" if terminado else f"{indice + 1}. {titulo}"
            ctk.CTkLabel(
                self.indicadores, text=texto,
                text_color=COLORES["acento"] if activo else COLORES["texto_suave"],
                font=("Segoe UI", 10, "bold" if activo or terminado else "normal"),
                fg_color=COLORES["acento_claro"] if activo else "transparent",
                corner_radius=8).pack(side="left", padx=(0, 8), ipady=6, ipadx=9)

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

        marco = ctk.CTkFrame(self.contenido_paso, fg_color="transparent")
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
            tarjeta = ctk.CTkFrame(
                marco,
                fg_color=COLORES["acento_claro"] if seleccionado else COLORES["tarjeta"],
                corner_radius=16, border_width=1,
                border_color=COLORES["acento"] if seleccionado else COLORES["borde"])
            tarjeta.grid(
                row=0, column=indice, padx=10, pady=18,
                sticky="nsew")
            ctk.CTkLabel(
                tarjeta, text="🏪" if tipo.casefold() == "establecimiento" else "📍",
                font=("Segoe UI Emoji", 28)).pack(
                    anchor="w", padx=18, pady=(18, 2))
            ctk.CTkLabel(
                tarjeta, text=titulo, text_color=COLORES["texto"],
                font=("Segoe UI", 16, "bold")).pack(
                    anchor="w", padx=18, pady=(6, 3))
            ctk.CTkLabel(
                tarjeta, text=descripcion, text_color=COLORES["texto_suave"],
                font=("Segoe UI", 11), wraplength=260, justify="left",
                anchor="w").pack(anchor="w", fill="x", expand=True, padx=18)
            ctk.CTkButton(
                tarjeta,
                text="Seleccionado" if seleccionado else "Seleccionar",
                height=36, corner_radius=9,
                fg_color=COLORES["acento"] if seleccionado else COLORES["tarjeta"],
                hover_color="#E66F10" if seleccionado else COLORES["acento_claro"],
                text_color="#FFFFFF" if seleccionado else COLORES["texto"],
                border_width=1 if not seleccionado else 0,
                border_color=COLORES["borde"],
                command=lambda valor=tipo: self._seleccionar_tipo(valor)
            ).pack(anchor="w", padx=18, pady=(16, 18))

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
            tarjeta = ctk.CTkFrame(
                interior,
                fg_color=COLORES["acento_claro"] if seleccionado else COLORES["tarjeta"],
                corner_radius=14, border_width=1,
                border_color=COLORES["acento"] if seleccionado else COLORES["borde"])
            tarjeta.grid(
                row=indice // 3, column=indice % 3,
                padx=8, pady=8, sticky="nsew")
            interior.columnconfigure(indice % 3, weight=1)
            ctk.CTkLabel(
                tarjeta, text=ICONOS_CATEGORIA.get(categoria, "📦"),
                font=("Segoe UI Emoji", 26)).pack(anchor="w", padx=16, pady=(16, 0))
            ctk.CTkLabel(
                tarjeta, text=categoria, text_color=COLORES["texto"],
                font=("Segoe UI", 13, "bold")).pack(
                    anchor="w", padx=16, pady=(7, 3))
            cantidad = sum(
                1 for datos in self.establecimientos.values()
                if datos.get("tipo") == categoria)
            ctk.CTkLabel(
                tarjeta, text=f"{cantidad} establecimiento(s)",
                text_color=COLORES["texto_suave"], font=("Segoe UI", 10)
            ).pack(anchor="w", padx=16)
            ctk.CTkButton(
                tarjeta,
                text="Seleccionada" if seleccionado else "Elegir categoría",
                height=34, corner_radius=8,
                fg_color=COLORES["acento"] if seleccionado else COLORES["tarjeta"],
                hover_color="#E66F10" if seleccionado else COLORES["acento_claro"],
                text_color="#FFFFFF" if seleccionado else COLORES["texto"],
                border_width=1 if not seleccionado else 0,
                border_color=COLORES["borde"],
                command=lambda valor=categoria: self._seleccionar_categoria(valor)
            ).pack(anchor="w", padx=16, pady=(12, 16))
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
            tarjeta = ctk.CTkFrame(
                interior,
                fg_color=COLORES["acento_claro"] if seleccionado else COLORES["tarjeta"],
                corner_radius=14, border_width=1,
                border_color=COLORES["acento"] if seleccionado else COLORES["borde"])
            tarjeta.grid(
                row=indice // 2, column=indice % 2,
                padx=8, pady=8, sticky="nsew")
            interior.columnconfigure(indice % 2, weight=1)
            ctk.CTkLabel(
                tarjeta, text=nombre, text_color=COLORES["texto"],
                font=("Segoe UI", 13, "bold"), wraplength=280,
                justify="left", anchor="w").pack(anchor="w", padx=16, pady=(16, 0))
            ctk.CTkLabel(
                tarjeta, text=datos["tipo"], text_color=COLORES["texto_suave"],
                font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(4, 0))
            productos = catalogo_para_establecimiento(nombre)
            ctk.CTkLabel(
                tarjeta,
                text=(f"{len(productos)} producto(s) disponibles"
                      if productos else "Catálogo sin productos disponibles"),
                text_color=COLORES["texto_suave"], font=("Segoe UI", 10)
            ).pack(anchor="w", padx=16, pady=(2, 0))
            ctk.CTkButton(
                tarjeta,
                text=("Seleccionado" if seleccionado else "Elegir establecimiento")
                if productos else "Sin productos",
                height=34, corner_radius=8,
                fg_color=COLORES["acento"] if productos else COLORES["borde"],
                hover_color="#E66F10" if productos else COLORES["borde"],
                text_color="#FFFFFF" if productos else COLORES["texto_suave"],
                font=("Segoe UI", 10, "bold"),
                command=lambda valor=nombre: self._seleccionar_establecimiento(valor),
                state="normal" if productos else "disabled",
            ).pack(anchor="w", padx=16, pady=(12, 16))
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

        barra = ctk.CTkFrame(
            self.contenido_paso, fg_color=COLORES["tarjeta"], corner_radius=12)
        barra.pack(fill="x", padx=8, pady=(0, 8))
        ctk.CTkLabel(
            barra, text="Buscar producto", text_color=COLORES["texto"],
            font=("Segoe UI", 11, "bold")).pack(side="left", padx=(14, 8), pady=10)
        self.ent_busqueda_producto = ctk.CTkEntry(
            barra, width=340, height=36, corner_radius=9,
            border_color=COLORES["borde"], fg_color=COLORES["fondo"],
            placeholder_text="Nombre del producto")
        self.ent_busqueda_producto.pack(side="left", fill="x", expand=True, padx=(0, 12), pady=8)
        limitar_campo(self.ent_busqueda_producto, MAX_TEXTO_SQL)
        self.ent_busqueda_producto.bind(
            "<KeyRelease>", lambda _evento: self._actualizar_lista_productos())

        self.marco_lista_productos = ctk.CTkFrame(
            self.contenido_paso, fg_color="transparent")
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
        tarjeta = ctk.CTkFrame(
            padre, fg_color=COLORES["acento_claro"] if seleccionado else COLORES["tarjeta"],
            corner_radius=14, border_width=1,
            border_color=COLORES["acento"] if seleccionado else COLORES["borde"],
            width=210, height=230)
        tarjeta.grid_propagate(False)

        imagen = ttk.Label(
            tarjeta, text="Cargando imagen...",
            style="TarjetaTexto.TLabel", anchor="center")
        imagen.pack(fill="both", expand=True)
        self._cargar_imagen(imagen, producto.get("imagen"))
        ctk.CTkLabel(
            tarjeta, text=producto["nombre"], text_color=COLORES["texto"],
            font=("Segoe UI", 12, "bold"), wraplength=190, justify="left"
        ).pack(anchor="w", padx=10, pady=(6, 0))
        ctk.CTkLabel(
            tarjeta, text=f"${producto['precio']:,.0f}",
            text_color=COLORES["texto"], font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(3, 0))
        ctk.CTkButton(
            tarjeta,
            text="Producto seleccionado" if seleccionado else "Seleccionar producto",
            height=32, corner_radius=8,
            fg_color=COLORES["acento"] if seleccionado else COLORES["acento"],
            hover_color="#E66F10", font=("Segoe UI", 10, "bold"),
            command=lambda item=producto: self._seleccionar_producto(item)
        ).pack(fill="x", padx=9, pady=(7, 8))
        self._registrar_rueda_recursivo(tarjeta, canvas)
        return tarjeta

    def _seleccionar_producto(self, producto):
        self.producto_actual = producto
        self._mostrar_paso()

    def _crear_zona_desplazable(self, dibujar, padre=None):
        padre = padre or self.contenido_paso
        zona = ctk.CTkFrame(
            padre, fg_color=COLORES["tarjeta"], corner_radius=12)
        zona.pack(fill="both", expand=True, padx=8, pady=4)
        canvas = tk.Canvas(
            zona, background=COLORES["tarjeta"], highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(
            zona, orientation="vertical", command=canvas.yview,
            width=12, corner_radius=8, fg_color=COLORES["tarjeta"],
            button_color=COLORES["borde"],
            button_hover_color=COLORES["acento"])
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

        marco = ctk.CTkFrame(
            self.contenido_paso, fg_color=COLORES["tarjeta"], corner_radius=14)
        marco.pack(fill="x", padx=8, pady=8)
        marco.columnconfigure(0, weight=1)
        marco.columnconfigure(1, weight=1)

        self.ent_desc_externa = self._entrada_estilizada(marco, "Ej. Recoger un paquete")
        self.ent_monto_externa = self._entrada_estilizada(marco, "Ej. 25000")
        self.ent_via = self._entrada_estilizada(marco, "Ej. Calle 5")
        self.ent_num = self._entrada_estilizada(marco, "Ej. 12-34")
        self.cmb_barrio = self._combo_estilizado(marco, list(self.barrios))

        self._campo(marco, "Descripción", self.ent_desc_externa, 0, 0)
        self._campo(marco, "Monto total ($)", self.ent_monto_externa, 0, 1)
        self._campo(marco, "Vía principal", self.ent_via, 2, 0)
        self._campo(marco, "Número", self.ent_num, 2, 1)
        self._campo(marco, "Barrio", self.cmb_barrio, 4, 0)
        ctk.CTkLabel(
            marco,
            text="Si tu barrio no aparece, todavía no tenemos cobertura allí.",
            text_color=COLORES["texto_suave"], font=("Segoe UI", 10),
            wraplength=500, anchor="w"
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
        ctk.CTkLabel(
            padre, text=titulo, text_color=COLORES["texto"],
            font=("Segoe UI", 11, "bold")
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
        except (InvalidOperation, ValueError):
            raise ValueError("El monto debe ser un número.")
        if not monto.is_finite():
            raise ValueError("El monto debe ser un número finito.")
        if monto <= 0:
            raise ValueError("El monto debe ser mayor que cero.")
        if not self.ent_via.get().strip() or not self.ent_num.get().strip():
            raise ValueError("Completa la vía principal y el número.")
        if not self.cmb_barrio.get():
            raise ValueError("Selecciona el barrio de recogida.")
        return descripcion, monto

    @staticmethod
    def _entrada_estilizada(padre, placeholder):
        return ctk.CTkEntry(
            padre, height=38, corner_radius=9, border_width=1,
            border_color=COLORES["borde"], fg_color=COLORES["fondo"],
            placeholder_text=placeholder)

    @staticmethod
    def _combo_estilizado(padre, valores):
        return ctk.CTkComboBox(
            padre, values=valores, state="readonly", height=38,
            corner_radius=9, border_width=1, border_color=COLORES["borde"],
            fg_color=COLORES["fondo"], button_color=COLORES["acento"],
            button_hover_color="#E66F10", dropdown_fg_color=COLORES["tarjeta"],
            dropdown_hover_color=COLORES["acento_claro"],
            text_color=COLORES["texto"])

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
        if self.pasos[self.indice_paso][0] == "confirmar":
            metodo = self.cmb_metodo.get().strip()
            if metodo in self.metodos:
                self.metodo_pago_actual = metodo
        self.indice_paso -= 1
        self._mostrar_paso()

    def _mostrar_confirmacion(self):
        self.lbl_paso.configure(text=f"{len(self.pasos)}. Revisa y envía tu solicitud")
        self.lbl_ayuda.configure(
            text="Verifica la información antes de enviarla.")

        marco = ctk.CTkFrame(
            self.contenido_paso, fg_color=COLORES["tarjeta"], corner_radius=14,
            border_width=1, border_color=COLORES["borde"])
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
            es_total = etiqueta in {"Total", "Monto"}
            ctk.CTkLabel(
                marco, text=etiqueta, text_color=COLORES["texto_suave"],
                font=("Segoe UI", 12 if es_total else 11,
                      "bold" if es_total else "normal")
            ).grid(row=fila, column=0, sticky="nw", padx=(0, 22), pady=5)
            ctk.CTkLabel(
                marco, text=valor,
                text_color=COLORES["acento"] if es_total else COLORES["texto"],
                font=("Segoe UI", 16 if es_total else 12, "bold"),
                wraplength=500, justify="left"
            ).grid(row=fila, column=1, sticky="w", pady=5)

        ttk.Separator(marco).grid(
            row=len(datos_resumen), column=0, columnspan=2,
            sticky="ew", pady=(12, 10))
        ctk.CTkLabel(
            marco, text="Método de pago", text_color=COLORES["texto"],
            font=("Segoe UI", 11, "bold")
        ).grid(row=len(datos_resumen) + 1, column=0,
               sticky="w", padx=(0, 22), pady=5)
        self.cmb_metodo = self._combo_estilizado(marco, list(self.metodos))
        self.cmb_metodo.grid(
            row=len(datos_resumen) + 1, column=1, sticky="w", pady=5)
        if self.metodo_pago_actual in self.metodos:
            self.cmb_metodo.set(self.metodo_pago_actual)
        elif "Efectivo" in self.metodos:
            self.cmb_metodo.set("Efectivo")
            self.metodo_pago_actual = "Efectivo"
        elif self.metodos:
            self.cmb_metodo.set(next(iter(self.metodos)))
            self.metodo_pago_actual = self.cmb_metodo.get()

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
        self.btn_continuar.configure(state="disabled", text="Enviando…")
        self.btn_atras.configure(state="disabled")
        ejecutar_en_segundo_plano(
            self,
            lambda: op.crear_solicitud(
                self.ventana.sesion["identificacion"], datos),
            self._solicitud_creada, self._fallo_creacion)

    def _solicitud_creada(self, numero):
        messagebox.showinfo(
            "Solicitud creada",
            f"Tu solicitud quedó registrada con el número {numero}.")
        self.ventana.mostrar_modulo("mis_solicitudes")

    def _fallo_creacion(self, error):
        self.btn_continuar.configure(
            state="normal", text="Enviar solicitud", command=self._crear)
        self.btn_atras.configure(state="normal" if self.indice_paso > 0 else "disabled")
        messagebox.showerror("No se pudo crear la solicitud", str(error))

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
        ancho = max(etiqueta.winfo_width(), 260)
        alto = max(etiqueta.winfo_height(), 112)
        remuestreos = getattr(Image, "Resampling", Image)
        remuestreo = getattr(remuestreos, "LANCZOS", 1)
        imagen = ImageOps.fit(
            imagen, (ancho, alto), method=remuestreo,
            centering=(0.5, 0.5))
        foto = ImageTk.PhotoImage(imagen)
        self.imagenes_cache[url] = foto
        etiqueta.configure(image=foto, text="")
        etiqueta.image = foto
