from tkinter import ttk, messagebox

from database.conexion import ErrorBD
from operaciones.accesos import (
    buscar_cliente, buscar_domiciliario, listar_barrios, listar_medios_transporte,
    registrar_cliente, registrar_domiciliario)

CAMPOS_CLIENTE = [
    ("identificacion", "Identificación", "entero", True),
    ("nombre", "Nombre", "texto", True),
    ("apellidoPaterno", "Apellido paterno", "texto", True),
    ("apellidoMaterno", "Apellido materno (opcional)", "texto", False),
    ("telefono", "Teléfono", "entero", True),
    ("correo", "Correo electrónico", "texto", True),
    ("viaPrincipal", "Vía principal (ej. Calle 49)", "texto", True),
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

MAX_INT = 2147483647


class PantallaAcceso(ttk.Frame):
    def __init__(self, parent, ventana=None, rol="cliente"):
        super().__init__(parent, style="Contenido.TFrame", padding=28)
        self.ventana = ventana
        self.rol = rol
        self.campos = CAMPOS_CLIENTE if rol == "cliente" else CAMPOS_DOMICILIARIO
        self.widgets = {}   #clave Entry / Combobox
        self.opciones = {}  # clave  {texto mostrado: id}

        ttk.Button(self, text="← Volver", style="Secundario.TButton",
                   command=ventana.mostrar_inicio).pack(anchor="w")
        nombre_rol = "clientes" if rol == "cliente" else "domiciliarios"
        ttk.Label(self, text=f"Acceso de {nombre_rol}",
                  style="Titulo.TLabel").pack(anchor="w", pady=(14, 0))
        ttk.Label(self, text="Ingresa con tu identificación o regístrate por primera vez.",
                  style="Subtitulo.TLabel").pack(anchor="w", pady=(2, 14))

        cuaderno = ttk.Notebook(self)
        cuaderno.pack(fill="both", expand=True)
        self._pestana_ingreso(cuaderno)
        self._pestana_registro(cuaderno)

    def _pestana_ingreso(self, cuaderno):
        marco = ttk.Frame(cuaderno, style="Tarjeta.TFrame", padding=24)
        cuaderno.add(marco, text="Ingresar")
        formulario = ttk.Frame(marco, style="Tarjeta.TFrame")
        formulario.place(relx=0.5, rely=0.5, anchor="center")
        ttk.Label(formulario, text="Número de identificación", style="Campo.TLabel").pack()
        self.ent_ingreso = ttk.Entry(formulario, width=30)
        self.ent_ingreso.pack(pady=(4, 14))
        self.ent_ingreso.bind("<Return>", lambda e: self._ingresar())
        ttk.Button(formulario, text="Ingresar", style="Accion.TButton",
                   command=self._ingresar).pack()

    def _ingresar(self):
        texto = self.ent_ingreso.get().strip()
        if not texto.isdigit():
            messagebox.showwarning("Identificación no válida", "Escribe solo números.")
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

    def _pestana_registro(self, cuaderno):
        marco = ttk.Frame(cuaderno, style="Tarjeta.TFrame", padding=24)
        cuaderno.add(marco, text="Registrarme")
        formulario = ttk.Frame(marco, style="Tarjeta.TFrame")
        formulario.place(relx=0.5, rely=0.5, anchor="center")
        self._cargar_opciones()

        for i, (clave, etiqueta, tipo, _) in enumerate(self.campos):
            fila, col = i // 2, (i % 2) * 2
            ttk.Label(formulario, text=etiqueta, style="Campo.TLabel").grid(
                row=fila * 2, column=col, sticky="w", padx=(0, 24), pady=(6, 0))
            if tipo == "combo":
                widget = ttk.Combobox(formulario, values=list(self.opciones.get(clave, {})),
                                      state="readonly", width=27)
            else:
                widget = ttk.Entry(formulario, width=30)
            widget.grid(row=fila * 2 + 1, column=col, sticky="w", padx=(0, 24), pady=(2, 6))
            self.widgets[clave] = widget

        filas = (len(self.campos) + 1) // 2
        ttk.Button(formulario, text="Registrarme", style="Accion.TButton",
                   command=self._registrar).grid(row=filas * 2 + 1, column=0,
                                                 columnspan=4, pady=(18, 0))

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
                valor = int(texto)
                if clave == "identificacion" and valor > MAX_INT:
                    raise ValueError(f"La identificación no puede superar {MAX_INT}.")
                datos[clave] = valor
            elif tipo == "combo":
                datos[clave] = self.opciones[clave][texto]
            else:
                if len(texto) > 50:
                    raise ValueError(f"«{nombre}» admite máximo 50 caracteres.")
                if clave == "correo" and "@" not in texto:
                    raise ValueError("Escribe un correo electrónico válido.")
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
            messagebox.showerror("No se pudo registrar", str(e))
            return
        messagebox.showinfo("Registro exitoso", f"Bienvenido(a), {datos['nombre']}.")
        self.ventana.iniciar_sesion(self.rol, datos["identificacion"], datos["nombre"])
