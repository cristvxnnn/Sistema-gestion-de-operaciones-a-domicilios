"""Módulos del rol cliente: resumen, mis solicitudes, crear solicitud y mis incidentes."""
from io import BytesIO
from decimal import Decimal, InvalidOperation
from threading import Thread
from tkinter import ttk, messagebox
from urllib.request import urlopen

from database.conexion import ErrorBD
from interfaces.panel_base import PanelBase
from interfaces.componentes import (
    TablaDatos, tarjeta_indicador, mostrar_error, limitar_campo)
from interfaces.validaciones import MAX_TEXTO_SQL
from operaciones import cliente as op
from operaciones.accesos import listar_barrios
from operaciones.catalogos import catalogo_para_establecimiento

try:
    from PIL import Image, ImageTk
except ImportError:  # Las imágenes son opcionales para poder usar el programa sin Pillow.
    Image = ImageTk = None


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
        self.catalogo_actual = {}
        self.carrito = []
        self._imagen_actual = None
        self._imagen_tk = None

        marco = ttk.Frame(self.contenido, style="Tarjeta.TFrame", padding=24)
        marco.pack(anchor="w")

        def etiqueta(texto, fila, col=0, padre=marco):
            ttk.Label(padre, text=texto, style="Campo.TLabel").grid(
                row=fila, column=col, sticky="w", padx=(0, 24), pady=(6, 0))

        etiqueta("Descripción", 0)
        self.ent_desc = ttk.Entry(marco, width=34)
        self.ent_desc.grid(row=1, column=0, sticky="w", padx=(0, 24), pady=(2, 6))
        limitar_campo(self.ent_desc, MAX_TEXTO_SQL)

        etiqueta("Monto total ($)", 0, 1)
        self.ent_monto = ttk.Entry(marco, width=20)
        self.ent_monto.grid(row=1, column=1, sticky="w", pady=(2, 6))
        limitar_campo(self.ent_monto, 13)

        etiqueta("Método de pago", 2)
        self.cmb_metodo = ttk.Combobox(marco, values=list(metodos), state="readonly", width=31)
        self.cmb_metodo.grid(row=3, column=0, sticky="w", padx=(0, 24), pady=(2, 6))
        etiqueta("Tipo de recogida", 2, 1)
        self.cmb_tipo = ttk.Combobox(marco, values=list(tipos), state="readonly", width=17)
        self.cmb_tipo.grid(row=3, column=1, sticky="w", pady=(2, 6))
        self.cmb_tipo.bind("<<ComboboxSelected>>", self._cambiar_tipo)

        # Zona dinámica: establecimiento con catálogo o dirección externa.
        self.marco_est = ttk.Frame(marco, style="Menu.TFrame")
        etiqueta("Establecimiento", 0, 0, self.marco_est)
        self.cmb_est = ttk.Combobox(
            self.marco_est, values=list(estabs), state="readonly", width=31)
        self.cmb_est.grid(row=1, column=0, sticky="w", pady=(2, 6))
        self.cmb_est.bind("<<ComboboxSelected>>", self._cargar_catalogo)

        self.marco_catalogo = ttk.Frame(self.marco_est, style="Menu.TFrame")
        ttk.Label(self.marco_catalogo, text="Producto", style="Campo.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 14))
        ttk.Label(self.marco_catalogo, text="Cantidad", style="Campo.TLabel").grid(
            row=0, column=1, sticky="w")
        self.cmb_producto = ttk.Combobox(
            self.marco_catalogo, state="readonly", width=24)
        self.cmb_producto.grid(row=1, column=0, sticky="w", padx=(0, 14), pady=(2, 6))
        self.cmb_producto.bind("<<ComboboxSelected>>", self._mostrar_producto)
        self.ent_cantidad = ttk.Entry(self.marco_catalogo, width=10)
        self.ent_cantidad.grid(row=1, column=1, sticky="w", pady=(2, 6))
        limitar_campo(self.ent_cantidad, 2, solo_numeros=True)
        self.ent_cantidad.insert(0, "1")
        ttk.Button(self.marco_catalogo, text="Agregar", style="Accion.TButton",
                   command=self._agregar_producto).grid(
                       row=1, column=2, padx=(12, 0), pady=(2, 6))

        self.lbl_precio = ttk.Label(
            self.marco_catalogo, text="", style="TarjetaTexto.TLabel")
        self.lbl_precio.grid(row=2, column=0, columnspan=3, sticky="w", pady=(2, 0))
        self.lbl_imagen = ttk.Label(
            self.marco_catalogo, text="Selecciona un producto para ver su imagen.",
            style="TarjetaTexto.TLabel")
        self.lbl_imagen.grid(row=3, column=0, columnspan=3, sticky="w", pady=(2, 6))

        self.tabla_carrito = ttk.Treeview(
            self.marco_catalogo, columns=("producto", "cantidad", "subtotal"),
            show="headings", height=3)
        for clave, titulo, ancho in (
                ("producto", "Producto", 180), ("cantidad", "Cantidad", 75),
                ("subtotal", "Subtotal", 95)):
            self.tabla_carrito.heading(clave, text=titulo)
            self.tabla_carrito.column(clave, width=ancho, anchor="w")
        self.tabla_carrito.grid(row=4, column=0, columnspan=3, sticky="w", pady=(2, 4))
        ttk.Button(self.marco_catalogo, text="Quitar seleccionado",
                   style="Secundario.TButton", command=self._quitar_producto).grid(
                       row=5, column=0, sticky="w", pady=(2, 6))
        self.marco_catalogo.grid(row=2, column=0, columnspan=3, sticky="w")
        self.marco_catalogo.grid_remove()

        self.marco_ext = ttk.Frame(marco, style="Menu.TFrame")
        etiqueta("Vía principal (ej. Calle 23)", 0, 0, self.marco_ext)
        self.ent_via = ttk.Entry(self.marco_ext, width=34)
        self.ent_via.grid(row=1, column=0, sticky="w", padx=(0, 24), pady=(2, 6))
        limitar_campo(self.ent_via, MAX_TEXTO_SQL)
        etiqueta("Número (ej. 17-20)", 0, 1, self.marco_ext)
        self.ent_num = ttk.Entry(self.marco_ext, width=20)
        self.ent_num.grid(row=1, column=1, sticky="w", pady=(2, 6))
        limitar_campo(self.ent_num, MAX_TEXTO_SQL)
        etiqueta("Barrio", 2, 0, self.marco_ext)
        self.cmb_barrio = ttk.Combobox(
            self.marco_ext, values=list(barrios), state="readonly", width=31)
        self.cmb_barrio.grid(row=3, column=0, sticky="w", pady=(2, 0))
        ttk.Label(
            self.marco_ext,
            text="Si tu barrio no aparece, todavía no tenemos cobertura allí.",
            style="TarjetaTexto.TLabel").grid(
                row=4, column=0, columnspan=2, sticky="w", pady=(3, 6))

        ttk.Button(marco, text="Crear solicitud", style="Accion.TButton",
                   command=self._crear).grid(row=6, column=0, sticky="w", pady=(18, 0))

    def _cambiar_tipo(self, _evento=None):
        self.marco_est.grid_remove()
        self.marco_ext.grid_remove()
        tipo = self.cmb_tipo.get()
        if tipo == "Establecimiento":
            self.marco_est.grid(row=4, column=0, columnspan=2, sticky="w")
            if self.cmb_est.get():
                self._cargar_catalogo()
            else:
                self._configurar_campos_catalogo(False)
        elif tipo == "Externa":
            self.catalogo_actual = {}
            self._configurar_campos_catalogo(False)
            self.marco_ext.grid(row=4, column=0, columnspan=2, sticky="w")

    def _configurar_entry(self, entry, valor="", solo_lectura=False):
        entry.configure(state="normal")
        entry.delete(0, "end")
        if valor:
            entry.insert(0, valor)
        if solo_lectura:
            entry.configure(state="readonly")

    def _configurar_campos_catalogo(self, activo):
        self.ent_desc.configure(state="normal")
        self.ent_monto.configure(state="normal")
        if activo:
            self.ent_desc.configure(state="readonly")
            self.ent_monto.configure(state="readonly")

    def _cargar_catalogo(self, _evento=None):
        productos = catalogo_para_establecimiento(self.cmb_est.get())
        self.catalogo_actual = {producto["nombre"]: producto for producto in productos}
        self.carrito = []
        self.tabla_carrito.delete(*self.tabla_carrito.get_children())
        self._configurar_campos_catalogo(bool(productos))
        if not productos:
            self.marco_catalogo.grid_remove()
            self._configurar_entry(self.ent_desc)
            self._configurar_entry(self.ent_monto)
            return
        self.cmb_producto.configure(values=list(self.catalogo_actual))
        self.cmb_producto.set("")
        self.lbl_precio.configure(text="")
        self.lbl_imagen.configure(
            image="", text="Selecciona un producto para ver su imagen.")
        self.marco_catalogo.grid()
        self._configurar_entry(self.ent_desc)
        self._configurar_entry(self.ent_monto)
        self._configurar_campos_catalogo(True)

    def _mostrar_producto(self, _evento=None):
        producto = self.catalogo_actual.get(self.cmb_producto.get())
        if not producto:
            return
        url = producto.get("imagen", "")
        self.lbl_precio.configure(text=f"Precio unitario: ${producto['precio']:,.0f}")
        self._imagen_actual = url
        self._imagen_tk = None
        if Image is None or ImageTk is None:
            self.lbl_imagen.configure(image="", text=f"Imagen: {url}")
            return
        self.lbl_imagen.configure(image="", text="Cargando imagen...")

        def descargar():
            try:
                with urlopen(url, timeout=5) as respuesta:
                    imagen = Image.open(BytesIO(respuesta.read())).convert("RGB")
                    imagen.thumbnail((160, 100))
            except Exception:
                imagen = None
            try:
                self.after(0, lambda: self._aplicar_imagen(imagen, url))
            except (RuntimeError, AttributeError):
                pass

        Thread(target=descargar, daemon=True).start()

    def _aplicar_imagen(self, imagen, url):
        if url != self._imagen_actual or not self.winfo_exists():
            return
        if imagen is None:
            self.lbl_imagen.configure(
                image="", text="No se pudo cargar la imagen de muestra.")
            return
        self._imagen_tk = ImageTk.PhotoImage(imagen)
        self.lbl_imagen.configure(image=self._imagen_tk, text="")

    def _agregar_producto(self):
        nombre = self.cmb_producto.get()
        if not nombre:
            messagebox.showwarning("Producto", "Selecciona un producto.")
            return
        cantidad_texto = self.ent_cantidad.get().strip()
        if not cantidad_texto.isdigit() or int(cantidad_texto) <= 0:
            messagebox.showwarning("Cantidad", "La cantidad debe ser un número mayor que cero.")
            return
        cantidad = int(cantidad_texto)
        producto = self.catalogo_actual[nombre]
        carrito_anterior = [item.copy() for item in self.carrito]
        for item in self.carrito:
            if item["nombre"] == nombre:
                item["cantidad"] += cantidad
                break
        else:
            self.carrito.append({
                "nombre": nombre,
                "precio": Decimal(str(producto["precio"])),
                "cantidad": cantidad,
            })
        if len(self._descripcion_carrito()) > MAX_TEXTO_SQL:
            self.carrito = carrito_anterior
            messagebox.showwarning(
                "Descripción demasiado larga",
                "La combinación de productos supera los 50 caracteres permitidos. "
                "Reduce cantidades o productos.")
            return
        self._actualizar_carrito()

    def _quitar_producto(self):
        seleccion = self.tabla_carrito.selection()
        if not seleccion:
            messagebox.showinfo("Productos", "Selecciona un producto para quitarlo.")
            return
        indice = int(seleccion[0])
        del self.carrito[indice]
        self._actualizar_carrito()

    def _actualizar_carrito(self):
        self.tabla_carrito.delete(*self.tabla_carrito.get_children())
        total = Decimal("0")
        for item in self.carrito:
            subtotal = item["precio"] * item["cantidad"]
            total += subtotal
            self.tabla_carrito.insert(
                "", "end",
                values=(item["nombre"], item["cantidad"], f"${subtotal:,.0f}"))
        self._configurar_entry(self.ent_desc, self._descripcion_carrito(), True)
        self._configurar_entry(self.ent_monto, f"{total:.2f}", True)

    def _descripcion_carrito(self):
        return ", ".join(
            f"{item['nombre']} x{item['cantidad']}" for item in self.carrito)

    def _leer(self):
        desc = self.ent_desc.get().strip()
        if not desc:
            raise ValueError("La descripción es obligatoria.")
        if len(desc) > MAX_TEXTO_SQL:
            raise ValueError(f"La descripción admite máximo {MAX_TEXTO_SQL} caracteres.")
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
            if self.catalogo_actual and not self.carrito:
                raise ValueError("Agrega al menos un producto del catálogo.")
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
