"""Ventana de perfil para clientes y domiciliarios."""
import customtkinter as ctk
from tkinter import messagebox, simpledialog

from database.conexion import ErrorBD
from interfaces.componentes import ejecutar_en_segundo_plano, limitar_campo
from interfaces.estilos import COLORES
from interfaces.validaciones import MAX_TEXTO_SQL, motivo_correo_invalido
from operaciones import accesos as op


class VentanaPerfil(ctk.CTkToplevel):
    """Muestra y edita los datos de los roles asociados al usuario."""

    def __init__(self, ventana):
        super().__init__(ventana)
        self.ventana = ventana
        self.identificacion = ventana.sesion["identificacion"]
        self.perfil = None
        self.barrios = {}
        self.medios = {}
        self.entradas = {}
        self.editando = False
        self.estado_var = ctk.IntVar(value=1)

        self.title("Mi perfil")
        self.geometry("700x700")
        self.resizable(False, False)
        self.configure(fg_color=COLORES["fondo"])
        self.transient(ventana)
        self.grab_set()

        self._construir_base()
        ejecutar_en_segundo_plano(
            self,
            lambda: self._cargar_datos(self.identificacion),
            self._cargar_perfil,
            self._mostrar_error,
        )

    def _construir_base(self):
        encabezado = ctk.CTkFrame(self, fg_color="transparent")
        encabezado.pack(fill="x", padx=24, pady=(20, 12))
        ctk.CTkLabel(
            encabezado, text="Mi perfil", text_color=COLORES["texto"],
            font=("Segoe UI", 24, "bold")).pack(anchor="w")
        self.lbl_subtitulo = ctk.CTkLabel(
            encabezado, text="Cargando tus datos…",
            text_color=COLORES["texto_suave"], font=("Segoe UI", 11),
            anchor="w")
        self.lbl_subtitulo.pack(anchor="w", pady=(3, 0))

        self.contenedor = ctk.CTkScrollableFrame(
            self, fg_color=COLORES["tarjeta"], corner_radius=14,
            border_width=1, border_color=COLORES["borde"])
        self.contenedor.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        self.acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.acciones.pack(fill="x", padx=24, pady=(0, 20))
        self.btn_cerrar = ctk.CTkButton(
            self.acciones, text="Cerrar", width=110, height=38,
            fg_color=COLORES["tarjeta"], hover_color=COLORES["acento_claro"],
            text_color=COLORES["texto"], border_width=1,
            border_color=COLORES["borde"], command=self.destroy)
        self.btn_cerrar.pack(side="right")

    @staticmethod
    def _cargar_datos(identificacion):
        perfil = op.obtener_perfil(identificacion)
        if perfil is None:
            raise ErrorBD("No se encontraron los datos del usuario.")
        barrios = op.listar_barrios() if perfil["esCliente"] else []
        medios = op.listar_medios_transporte() if perfil["esDomiciliario"] else []
        return perfil, barrios, medios

    def _cargar_perfil(self, resultado):
        self.perfil, barrios, medios = resultado
        self.barrios = {
            fila["nombreBarrio"]: fila["idBarrio"] for fila in barrios
        }
        self.medios = {
            fila["nombreMedioTransporte"]: fila["idMedioTransporte"]
            for fila in medios
        }
        self._dibujar_perfil()

    def _mostrar_error(self, error):
        messagebox.showerror("No se pudo cargar el perfil", str(error), parent=self)
        self.destroy()

    def _limpiar_contenedor(self):
        for hijo in self.contenedor.winfo_children():
            hijo.destroy()
        self.entradas = {}

    def _seccion(self, texto):
        ctk.CTkLabel(
            self.contenedor, text=texto, text_color=COLORES["texto"],
            font=("Segoe UI", 15, "bold"), anchor="w").pack(
                fill="x", padx=18, pady=(16, 8))

    def _entrada(self, clave, etiqueta, valor="", fila=0, columna=0,
                 solo_lectura=False, parent=None):
        parent = parent or self.contenedor
        bloque = ctk.CTkFrame(parent, fg_color="transparent")
        bloque.grid(row=fila, column=columna, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(
            bloque, text=etiqueta, text_color=COLORES["texto"],
            font=("Segoe UI", 10, "bold"), anchor="w").pack(
                anchor="w", pady=(0, 4))
        entrada = ctk.CTkEntry(
            bloque, height=38, corner_radius=9,
            border_color=COLORES["borde"], fg_color=COLORES["fondo"],
            text_color=COLORES["texto"])
        entrada.pack(fill="x")
        if valor is not None:
            entrada.insert(0, str(valor))
        entrada.configure(state="disabled")
        self.entradas[clave] = entrada
        return entrada

    def _combo(self, clave, etiqueta, valores, valor="", fila=0, columna=0,
               parent=None):
        parent = parent or self.contenedor
        bloque = ctk.CTkFrame(parent, fg_color="transparent")
        bloque.grid(row=fila, column=columna, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(
            bloque, text=etiqueta, text_color=COLORES["texto"],
            font=("Segoe UI", 10, "bold"), anchor="w").pack(
                anchor="w", pady=(0, 4))
        combo = ctk.CTkComboBox(
            bloque, values=list(valores), state="readonly", height=38,
            corner_radius=9, border_width=1,
            border_color=COLORES["borde"], fg_color=COLORES["fondo"],
            button_color=COLORES["acento"],
            button_hover_color="#E66F10",
            dropdown_fg_color=COLORES["tarjeta"],
            dropdown_hover_color=COLORES["acento_claro"],
            text_color=COLORES["texto"])
        combo.pack(fill="x")
        if valor:
            combo.set(valor)
        combo.configure(state="disabled")
        self.entradas[clave] = combo
        return combo

    def _datos_rol(self, texto):
        marco = ctk.CTkFrame(
            self.contenedor, fg_color=COLORES["acento_claro"],
            corner_radius=10)
        marco.pack(fill="x", padx=18, pady=(4, 8))
        ctk.CTkLabel(
            marco, text=texto, text_color=COLORES["acento"],
            font=("Segoe UI", 10, "bold")).pack(
                anchor="w", padx=12, pady=8)

    def _dibujar_perfil(self):
        self._limpiar_contenedor()
        p = self.perfil
        self.lbl_subtitulo.configure(
            text="Consulta y administra la información de tu cuenta.")

        self._seccion("Datos personales")
        datos = ctk.CTkFrame(self.contenedor, fg_color="transparent")
        datos.pack(fill="x", padx=8)
        datos.grid_columnconfigure((0, 1), weight=1)

        self._entrada(
            "identificacion", "Identificación", p["identificacion"],
            fila=0, columna=0, solo_lectura=True, parent=datos)
        self._entrada(
            "nombre", "Nombre", p["nombre"], fila=0, columna=1, parent=datos)
        self._entrada(
            "apellidoPaterno", "Apellido paterno", p["apellidoPaterno"],
            fila=1, columna=0, parent=datos)
        self._entrada(
            "apellidoMaterno", "Apellido materno", p["apellidoMaterno"] or "",
            fila=1, columna=1, parent=datos)
        self._entrada(
            "telefono", "Teléfono", p["telefono"], fila=2, columna=0,
            parent=datos)
        self._entrada(
            "correo", "Correo electrónico", p["correo"], fila=2, columna=1,
            parent=datos)

        if p["esCliente"]:
            self._datos_rol("Datos de cliente")
            cliente = ctk.CTkFrame(self.contenedor, fg_color="transparent")
            cliente.pack(fill="x", padx=8)
            cliente.grid_columnconfigure((0, 1), weight=1)
            self._entrada(
                "viaPrincipal", "Vía principal", p["viaPrincipal"],
                fila=0, columna=0, parent=cliente)
            self._entrada(
                "numero", "Número", p["numero"], fila=0, columna=1,
                parent=cliente)
            self._combo(
                "idBarrio", "Barrio", self.barrios,
                p["nombreBarrio"] or "", fila=1, columna=0, parent=cliente)
            self._entrada(
                "referencia", "Referencia", p["referencia"] or "",
                fila=1, columna=1, parent=cliente)

        if p["esDomiciliario"]:
            self._datos_rol("Datos de domiciliario")
            domiciliario = ctk.CTkFrame(
                self.contenedor, fg_color="transparent")
            domiciliario.pack(fill="x", padx=8)
            domiciliario.grid_columnconfigure((0, 1), weight=1)
            self._entrada(
                "codigoDomiciliario", "Código de domiciliario",
                p["codigoDomiciliario"], fila=0, columna=0,
                solo_lectura=True, parent=domiciliario)
            self._combo(
                "idMedioTransporte", "Medio de transporte", self.medios,
                p["nombreMedioTransporte"] or "", fila=0, columna=1,
                parent=domiciliario)

            estado = ctk.CTkFrame(
                domiciliario, fg_color="transparent")
            estado.grid(row=1, column=0, columnspan=2,
                        sticky="ew", padx=10, pady=8)
            ctk.CTkLabel(
                estado, text="Estado del domiciliario",
                text_color=COLORES["texto"],
                font=("Segoe UI", 10, "bold")).pack(anchor="w")
            self.estado_var.set(int(p["idEstadoDomiciliario"] or 1))
            self.switch_estado = ctk.CTkSwitch(
                estado,
                text="Activo" if self.estado_var.get() == 1 else "Inactivo",
                variable=self.estado_var, onvalue=1, offvalue=2,
                state="disabled", progress_color="#00D45A",
                button_color="#FFFFFF", button_hover_color="#F1F5F9",
                command=self._actualizar_texto_estado)
            self.switch_estado.pack(anchor="w", pady=(8, 0))

        self._actualizar_acciones()

    def _actualizar_acciones(self):
        for hijo in self.acciones.winfo_children():
            if hijo is not self.btn_cerrar:
                hijo.destroy()
        if self.editando:
            self.btn_guardar = ctk.CTkButton(
                self.acciones, text="Guardar cambios", width=150, height=38,
                fg_color=COLORES["acento"], hover_color="#E66F10",
                command=self._guardar)
            self.btn_guardar.pack(side="right", padx=(0, 10))
            self.btn_cancelar = ctk.CTkButton(
                self.acciones, text="Cancelar", width=110, height=38,
                fg_color=COLORES["tarjeta"],
                hover_color=COLORES["acento_claro"],
                text_color=COLORES["texto"], border_width=1,
                border_color=COLORES["borde"], command=self._cancelar_edicion)
            self.btn_cancelar.pack(side="right", padx=(0, 10))
        else:
            self.btn_editar = ctk.CTkButton(
                self.acciones, text="Modificar datos personales",
                width=205, height=38, fg_color=COLORES["acento"],
                hover_color="#E66F10", command=self._editar)
            self.btn_editar.pack(side="left")
            tiene_otro_rol = (
                (self.ventana.sesion["rol"] == "cliente" and self.perfil["esDomiciliario"])
                or (self.ventana.sesion["rol"] == "domiciliario" and self.perfil["esCliente"]))
            self.btn_eliminar = ctk.CTkButton(
                self.acciones,
                text="Eliminar rol actual" if tiene_otro_rol else "Eliminar cuenta",
                width=165 if tiene_otro_rol else 145, height=38,
                fg_color="#B42318", hover_color="#8F1D14",
                command=self._confirmar_eliminacion)
            self.btn_eliminar.pack(side="left", padx=10)

    def _editar(self):
        self.editando = True
        for clave, widget in self.entradas.items():
            if clave != "identificacion" and clave != "codigoDomiciliario":
                widget.configure(state="normal" if clave not in {
                    "idBarrio", "idMedioTransporte"} else "readonly")
        if hasattr(self, "switch_estado"):
            self.switch_estado.configure(state="normal")
        self._actualizar_acciones()

    def _cancelar_edicion(self):
        self.editando = False
        self._dibujar_perfil()

    def _actualizar_texto_estado(self):
        if hasattr(self, "switch_estado"):
            self.switch_estado.configure(
                text="Activo" if self.estado_var.get() == 1 else "Inactivo")

    def _leer_datos(self):
        p = self.perfil
        datos = {
            "identificacion": int(p["identificacion"]),
            "nombre": self.entradas["nombre"].get().strip(),
            "apellidoPaterno": self.entradas["apellidoPaterno"].get().strip(),
            "apellidoMaterno": self.entradas["apellidoMaterno"].get().strip() or None,
            "telefono": self.entradas["telefono"].get().strip(),
            "correo": self.entradas["correo"].get().strip(),
            "esCliente": bool(p["esCliente"]),
            "esDomiciliario": bool(p["esDomiciliario"]),
        }
        if not datos["nombre"] or not datos["apellidoPaterno"]:
            raise ValueError("El nombre y el apellido paterno son obligatorios.")
        if not datos["telefono"].isdigit():
            raise ValueError("El teléfono debe contener solo números.")
        error_correo = motivo_correo_invalido(datos["correo"])
        if error_correo:
            raise ValueError(error_correo)
        for clave in ("nombre", "apellidoPaterno", "apellidoMaterno"):
            if datos[clave] and len(datos[clave]) > MAX_TEXTO_SQL:
                raise ValueError(f"El campo «{clave}» supera el límite permitido.")

        datos["telefono"] = int(datos["telefono"])
        if datos["esCliente"]:
            barrio = self.entradas["idBarrio"].get()
            datos.update({
                "viaPrincipal": self.entradas["viaPrincipal"].get().strip(),
                "numero": self.entradas["numero"].get().strip(),
                "idBarrio": self.barrios.get(barrio),
                "referencia": self.entradas["referencia"].get().strip() or None,
            })
            if not datos["viaPrincipal"] or not datos["numero"] or not datos["idBarrio"]:
                raise ValueError("Completa la dirección y el barrio.")
        if datos["esDomiciliario"]:
            medio = self.entradas["idMedioTransporte"].get()
            datos.update({
                "idMedioTransporte": self.medios.get(medio),
                "idEstadoDomiciliario": int(self.estado_var.get()),
            })
            if not datos["idMedioTransporte"]:
                raise ValueError("Selecciona el medio de transporte.")
        return datos

    def _guardar(self):
        try:
            datos = self._leer_datos()
        except ValueError as error:
            messagebox.showwarning("Revisa los datos", str(error), parent=self)
            return
        self.btn_guardar.configure(state="disabled", text="Guardando…")
        ejecutar_en_segundo_plano(
            self, lambda: op.actualizar_perfil(datos),
            lambda _resultado: self._guardado(datos),
            self._mostrar_error_guardado)

    def _guardado(self, datos):
        self.ventana.sesion["nombre"] = datos["nombre"]
        avatar = getattr(self.ventana, "lbl_avatar", None)
        if avatar is not None and avatar.winfo_exists():
            avatar.configure(text=(datos["nombre"] or "?")[0].upper())
        if getattr(self.ventana, "lbl_nombre_perfil", None) is not None:
            self.ventana.lbl_nombre_perfil.configure(text=datos["nombre"])
        self.editando = False
        ejecutar_en_segundo_plano(
            self, lambda: self._cargar_datos(self.identificacion),
            self._cargar_perfil,
            self._mostrar_error)

    def _mostrar_error_guardado(self, error):
        if hasattr(self, "btn_guardar"):
            self.btn_guardar.configure(state="normal", text="Guardar cambios")
        messagebox.showerror("No se pudieron guardar los cambios",
                             str(error), parent=self)

    def _confirmar_eliminacion(self):
        rol = self.ventana.sesion["rol"]
        conserva_otro_rol = (
            (rol == "cliente" and self.perfil["esDomiciliario"])
            or (rol == "domiciliario" and self.perfil["esCliente"]))
        if rol == "cliente":
            detalle = "Se eliminarán tus solicitudes e incidentes como cliente."
        else:
            detalle = (
                "Se eliminará tu rol de domiciliario. Si hay solicitudes asociadas "
                "a esta identificación, la operación no podrá completarse.")
        if conserva_otro_rol:
            rol_restante = "domiciliario" if rol == "cliente" else "cliente"
            detalle += f"\n\nSe conservarán tus datos personales y tu rol de {rol_restante}."
        else:
            detalle += "\n\nSe eliminará también tu cuenta y tus datos personales."
        confirmado = messagebox.askyesno(
            "Eliminar rol" if conserva_otro_rol else "Eliminar cuenta",
            f"{detalle}\n\nEsta acción no se puede deshacer. ¿Deseas continuar?",
            icon="warning", parent=self)
        if not confirmado:
            return
        escrito = simpledialog.askstring(
            "Confirmar eliminación",
            "Escribe tu número de identificación para confirmar:",
            parent=self)
        if escrito != str(self.identificacion):
            messagebox.showwarning(
                "Eliminación cancelada",
                "La identificación no coincide.", parent=self)
            return
        ejecutar_en_segundo_plano(
            self, lambda: op.eliminar_cuenta(self.identificacion, rol),
            lambda _resultado: self._cuenta_eliminada(rol, conserva_otro_rol),
            lambda error: messagebox.showerror(
                "No se pudo eliminar la cuenta", str(error), parent=self))

    def _cuenta_eliminada(self, rol, conserva_otro_rol):
        self.grab_release()
        self.destroy()
        if conserva_otro_rol:
            rol_restante = "domiciliario" if rol == "cliente" else "cliente"
            messagebox.showinfo(
                "Rol eliminado",
                f"Se eliminó tu rol de {rol}. Tu rol de {rol_restante} se conservó.")
        self.ventana.cerrar_sesion()
