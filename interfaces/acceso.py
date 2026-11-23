import customtkinter as ctk
from tkinter import messagebox

from database.conexion import ErrorBD
from interfaces.estilos import COLORES
from interfaces.componentes import limitar_campo
from interfaces.validaciones import (
    MAX_BIGINT, MAX_IDENTIFICACION, MAX_TEXTO_SQL, motivo_correo_invalido,
    mensaje_error_registro, validar_identificacion)
from operaciones.accesos import (
    buscar_cliente, buscar_domiciliario, buscar_usuario, listar_barrios,
    listar_medios_transporte, registrar_cliente, registrar_domiciliario)

CAMPOS_CLIENTE = [
    ("identificacion", "Identificación", "entero", True),
    ("nombre", "Nombre", "texto", True),
    ("apellidoPaterno", "Apellido paterno", "texto", True),
    ("apellidoMaterno", "Apellido materno (opcional)", "texto", False),
    ("telefono", "Teléfono", "entero", True),
    ("correo", "Correo electrónico", "texto", True),
    ("viaPrincipal", "Dirección de entrega: Vía principal (ej. Calle 49)", "texto", True),
    ("numero", "Número (ej. 13-22)", "texto", True),
    ("idBarrio", "Barrio", "combo", True),
    ("referencia", "Referencia (opcional)", "texto", False),
]

CAMPOS_DOMICILIARIO = [
    ("identificacion", "Identificación", "entero", True),
    ("nombre", "Nombre", "texto", True),
    ("apellidoPaterno", "Apellido paterno", "texto", True),
    ("apellidoMaterno", "Apellido materno (opcional)", "texto", False),
    ("telefono", "Teléfono", "entero", True),
    ("correo", "Correo electrónico", "texto", True),
    ("idMedioTransporte", "Medio de transporte", "combo", True),
]

class PantallaAcceso(ctk.CTkFrame):
    def __init__(self, parent, ventana=None, rol="cliente"):
        super().__init__(parent, fg_color=COLORES["fondo"], corner_radius=0)
        self.ventana = ventana
        self.rol = rol
        self.campos = CAMPOS_CLIENTE if rol == "cliente" else CAMPOS_DOMICILIARIO
        self.widgets = {}   #clave Entry / Combobox
        self.opciones = {}  # clave  {texto mostrado: id}

        encabezado = ctk.CTkFrame(self, fg_color="transparent")
        encabezado.pack(fill="x", padx=30, pady=(22, 10))
        ctk.CTkButton(
            encabezado, text="←  Volver", width=110, height=36,
            corner_radius=10, fg_color=COLORES["tarjeta"],
            hover_color=COLORES["acento_claro"], text_color=COLORES["texto"],
            border_width=1, border_color=COLORES["borde"],
            command=ventana.mostrar_inicio).pack(anchor="w")
        nombre_rol = "cliente" if rol == "cliente" else "domiciliario"
        ctk.CTkLabel(
            encabezado, text=f"Acceso de {nombre_rol}",
            text_color=COLORES["texto"],
            font=("Segoe UI", 25, "bold")).pack(anchor="w", pady=(14, 2))
        ctk.CTkLabel(
            encabezado, text="Ingresa con tu identificación o crea una cuenta.",
            text_color=COLORES["texto_suave"],
            font=("Segoe UI", 12)).pack(anchor="w")

        self.cuaderno = ctk.CTkTabview(
            self, height=640, corner_radius=16, border_width=1,
            border_color=COLORES["borde"], fg_color=COLORES["tarjeta"],
            segmented_button_fg_color="#EDF1F6",
            segmented_button_selected_color=COLORES["acento"],
            segmented_button_selected_hover_color="#E66F10",
            segmented_button_unselected_color="#EDF1F6",
            segmented_button_unselected_hover_color=COLORES["acento_claro"],
            text_color=COLORES["texto"])
        self.cuaderno.pack(fill="both", expand=True, padx=30, pady=(8, 24))
        self.cuaderno.add("Ingresar")
        self.cuaderno.add("Registrarme")
        # CTkTabview no expone el tamaño de las pestañas en su constructor.
        self.cuaderno._segmented_button.configure(width=320, height=42)
        self._pestana_ingreso(self.cuaderno.tab("Ingresar"))
        self._pestana_registro(self.cuaderno.tab("Registrarme"))

    def _pestana_ingreso(self, marco):
        formulario = ctk.CTkFrame(
            marco, width=500, height=350,
            fg_color=COLORES["fondo"], corner_radius=16)
        formulario.pack_propagate(False)
        formulario.place(relx=0.5, rely=0.48, anchor="center")
        ctk.CTkLabel(
            formulario, text="¡Qué gusto verte!", text_color=COLORES["texto"],
            font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=28, pady=(24, 4))
        ctk.CTkLabel(
            formulario, text="Escribe tu identificación para continuar.",
            text_color=COLORES["texto_suave"], font=("Segoe UI", 11)).pack(
                anchor="w", padx=28, pady=(0, 16))
        ctk.CTkLabel(
            formulario, text="Número de identificación",
            text_color=COLORES["texto"], font=("Segoe UI", 11, "bold")).pack(
                anchor="w", padx=28)
        self.ent_ingreso = ctk.CTkEntry(
            formulario, width=400, height=44, corner_radius=10,
            border_width=1, border_color=COLORES["borde"],
            fg_color=COLORES["tarjeta"],
            placeholder_text="Ingresa tu número")
        self.ent_ingreso.pack(padx=40, pady=(6, 16))
        limitar_campo(self.ent_ingreso, MAX_IDENTIFICACION, solo_numeros=True)
        self.ent_ingreso.bind("<Return>", lambda e: self._ingresar())
        ctk.CTkButton(
            formulario, text="Ingresar  →", width=400, height=46,
            corner_radius=10, fg_color=COLORES["acento"],
            hover_color="#E66F10", font=("Segoe UI", 12, "bold"),
            command=self._ingresar).pack(padx=40, pady=(0, 26))

    def _ingresar(self):
        texto = self.ent_ingreso.get().strip()
        error_identificacion = validar_identificacion(texto)
        if error_identificacion:
            messagebox.showwarning("Identificación no válida", error_identificacion)
            return
        try:
            if self.rol == "cliente":
                usuario = buscar_cliente(int(texto))
            else:
                usuario = buscar_domiciliario(int(texto))
        except ErrorBD as e:
            messagebox.showerror("Error de base de datos", str(e))
            return
        if usuario is None:
            messagebox.showinfo("No registrado",
                                "No encontramos esa identificación. Puedes registrarte en la otra pestaña.")
            return
        self.ventana.iniciar_sesion(self.rol, usuario["identificacion"], usuario["nombre"])

    def _pestana_registro(self, marco):
        self._cargar_opciones()
        formulario = ctk.CTkScrollableFrame(
            marco, fg_color=COLORES["fondo"], corner_radius=14)
        formulario.pack(fill="both", expand=True, padx=12, pady=12)
        formulario.grid_columnconfigure((0, 1), weight=1)
        
        for i, (clave, etiqueta, tipo, _) in enumerate(self.campos):
            fila, col = i // 2, i % 2
            bloque = ctk.CTkFrame(formulario, fg_color="transparent")
            bloque.grid(row=fila, column=col, sticky="ew", padx=18, pady=8)
            bloque.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                bloque, text=etiqueta, text_color=COLORES["texto"],
                font=("Segoe UI", 11, "bold"), anchor="w").grid(
                    row=0, column=0, sticky="w", pady=(0, 5))
            if tipo == "combo":
                widget = ctk.CTkComboBox(
                    bloque, values=list(self.opciones.get(clave, {})),
                    state="readonly", height=40, corner_radius=10,
                    border_width=1, border_color=COLORES["borde"],
                    fg_color=COLORES["tarjeta"],
                    button_color=COLORES["acento"],
                    button_hover_color="#E66F10",
                    dropdown_fg_color=COLORES["tarjeta"],
                    dropdown_hover_color=COLORES["acento_claro"],
                    text_color=COLORES["texto"])
            else:
                widget = ctk.CTkEntry(
                    bloque, height=40, corner_radius=10, border_width=1,
                    border_color=COLORES["borde"], fg_color=COLORES["tarjeta"],
                    placeholder_text="Opcional" if "opcional" in etiqueta else "Escribe aquí")
                if clave == "identificacion":
                    limitar_campo(widget, MAX_IDENTIFICACION, solo_numeros=True)
                elif clave == "telefono":
                    limitar_campo(widget, MAX_BIGINT, solo_numeros=True)
                else:
                    limitar_campo(widget, MAX_TEXTO_SQL)
            widget.grid(row=1, column=0, sticky="ew")
            self.widgets[clave] = widget
            if clave == "identificacion":
                widget.bind("<FocusOut>", self._autocompletar_usuario)
                widget.bind("<Return>", self._autocompletar_usuario)

        filas = (len(self.campos) + 1) // 2
        self.etiqueta_autocompletar = ctk.CTkLabel(
            formulario, text="", text_color=COLORES["texto_suave"],
            font=("Segoe UI", 10), anchor="w")
        self.etiqueta_autocompletar.grid(
            row=filas, column=0, columnspan=2, sticky="w", padx=18, pady=(5, 0))

        fila_boton = filas + 1
        if self.rol == "cliente":
            ctk.CTkLabel(
                formulario,
                text="Si tu barrio no aparece, todavía no tenemos cobertura allí.",
                text_color=COLORES["texto_suave"],
                font=("Segoe UI", 10)).grid(
                    row=filas + 1, column=0, columnspan=2,
                    sticky="w", padx=18, pady=(5, 0))
            fila_boton += 1
        ctk.CTkButton(
            formulario, text="Crear cuenta", height=42, corner_radius=10,
            fg_color=COLORES["acento"], hover_color="#E66F10",
            font=("Segoe UI", 12, "bold"),
            command=self._registrar).grid(
                row=fila_boton, column=0, columnspan=2,
                padx=18, pady=(16, 20), sticky="ew")

    def _autocompletar_usuario(self, _evento=None):
        identificacion = self.widgets["identificacion"].get().strip()
        if not identificacion or not identificacion.isdigit():
            self.etiqueta_autocompletar.configure(text="")
            return
        error_identificacion = validar_identificacion(identificacion)
        if error_identificacion:
            self.etiqueta_autocompletar.configure(text="")
            return
        try:
            usuario = buscar_usuario(int(identificacion))
        except ErrorBD as e:
            self.etiqueta_autocompletar.configure(text="")
            messagebox.showerror("Error de base de datos", str(e))
            return

        if usuario is None:
            self.etiqueta_autocompletar.configure(
                text="No encontramos esa identificación; completa tus datos personales.")
            return

        for campo in ("nombre", "apellidoPaterno", "apellidoMaterno", "telefono", "correo"):
            widget = self.widgets.get(campo)
            if widget is not None:
                widget.delete(0, "end")
                widget.insert(0, str(usuario.get(campo) or ""))
        self.etiqueta_autocompletar.configure(
            text="Datos encontrados. Completamos tu información personal.")

    def _cargar_opciones(self):
        try:
            if self.rol == "cliente":
                filas = listar_barrios()
                self.opciones["idBarrio"] = {f["nombreBarrio"]: f["idBarrio"] for f in filas}
            else:
                filas = listar_medios_transporte()
                self.opciones["idMedioTransporte"] = {
                    f["nombreMedioTransporte"]: f["idMedioTransporte"] for f in filas}
        except ErrorBD as e:
            messagebox.showwarning("Sin datos", f"No se pudieron cargar las listas:\n{e}")

    def _leer_formulario(self):
        datos = {}
        for clave, etiqueta, tipo, obligatorio in self.campos:
            nombre = etiqueta.replace(" (opcional)", "")
            texto = self.widgets[clave].get().strip()
            if not texto:
                if obligatorio:
                    raise ValueError(f"El campo «{nombre}» es obligatorio.")
                datos[clave] = None
                continue
            if tipo == "entero":
                if not texto.isdigit():
                    raise ValueError(f"«{nombre}» debe contener solo números.")
                if clave == "identificacion":
                    error_identificacion = validar_identificacion(texto)
                    if error_identificacion:
                        raise ValueError(error_identificacion)
                valor = int(texto)
                datos[clave] = valor
            elif tipo == "combo":
                datos[clave] = self.opciones[clave][texto]
            else:
                if len(texto) > MAX_TEXTO_SQL:
                    raise ValueError(f"«{nombre}» admite máximo {MAX_TEXTO_SQL} caracteres.")
                if clave == "correo":
                    error_correo = motivo_correo_invalido(texto)
                    if error_correo:
                        raise ValueError(error_correo)
                datos[clave] = texto
        return datos

    def _registrar(self):
        try:
            datos = self._leer_formulario()
        except ValueError as e:
            messagebox.showwarning("Revisa el formulario", str(e))
            return
        try:
            if self.rol == "cliente":
                registrar_cliente(datos)
            else:
                registrar_domiciliario(datos)
        except ErrorBD as e:
            mensaje = mensaje_error_registro(e)
            if mensaje != str(e):
                messagebox.showerror("Correo ya registrado", mensaje)
                self.widgets["correo"].focus_set()
            else:
                messagebox.showerror("No se pudo registrar", mensaje)
            return
        messagebox.showinfo("Registro exitoso", f"Bienvenido(a), {datos['nombre']}.")
        self.ventana.iniciar_sesion(self.rol, datos["identificacion"], datos["nombre"])
