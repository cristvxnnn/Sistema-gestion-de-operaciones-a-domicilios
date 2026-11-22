import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox

from database.conexion import probar_conexion
from interfaces.estilos import aplicar_estilos, COLORES
from interfaces.inicio import PantallaInicio
from interfaces.acceso import PantallaAcceso
from interfaces.perfil import VentanaPerfil
from interfaces.menus import MENUS, TITULOS_ROL
from interfaces.componentes import ejecutar_en_segundo_plano


class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        ctk.set_widget_scaling(1.08)
        super().__init__()
        self.title("DOMIYA · Domicilios en Cali")
        ancho = min(1366, self.winfo_screenwidth() - 40)
        alto = min(820, self.winfo_screenheight() - 80)
        posicion_x = max((self.winfo_screenwidth() - ancho) // 2, 0)
        posicion_y = max((self.winfo_screenheight() - alto) // 2, 0)
        self.geometry(f"{ancho}x{alto}+{posicion_x}+{posicion_y}")
        self.resizable(False, False)
        aplicar_estilos(self)

        self.sesion = None          # {"rol", "identificacion", "nombre"} o None
        self._actual = None         # widget que se está mostrando
        self._botones = {}          # clave de módulo -> botón del menú

        self._crear_barra_estado()
        self.menu = ctk.CTkFrame(
            self, width=236, corner_radius=0, fg_color=COLORES["menu"])
        self.area = ctk.CTkFrame(
            self, corner_radius=0, fg_color=COLORES["fondo"])
        self.area.pack(side="left", fill="both", expand=True)

        self.mostrar_inicio()
        self.after(150, self._verificar_conexion)

    def _crear_barra_estado(self):
        barra = ctk.CTkFrame(
            self, height=30, corner_radius=0, fg_color=COLORES["fondo"])
        barra.pack(side="bottom", fill="x")
        barra.pack_propagate(False)
        self.lbl_conexion = ctk.CTkLabel(
            barra, text="●  Base de datos: sin conexión",
            text_color=COLORES["texto_suave"], font=("Segoe UI", 10))
        self.lbl_conexion.pack(side="left", padx=20, pady=3)

    def actualizar_estado_conexion(self, texto):
        conectado = texto.startswith("Base de datos: conectado")
        marca = "●" if conectado else "●"
        self.lbl_conexion.configure(
            text=f"{marca}  {texto}",
            text_color="#16A36A" if conectado else COLORES["texto_suave"])

    def _verificar_conexion(self):
        self.actualizar_estado_conexion("Base de datos: verificando conexión…")
        ejecutar_en_segundo_plano(
            self, probar_conexion, self._actualizar_conexion, self._error_conexion)

    def _actualizar_conexion(self, resultado):
        ok, mensaje = resultado
        if ok:
            self.actualizar_estado_conexion(f"Base de datos: conectado — {mensaje}")
        else:
            self.actualizar_estado_conexion("Base de datos: sin conexión")
            messagebox.showwarning("Sin conexión", mensaje)

    def _error_conexion(self, error):
        self.actualizar_estado_conexion("Base de datos: sin conexión")
        messagebox.showwarning("Sin conexión", str(error))

    def _reemplazar(self, clase, **kwargs):
        """Destruye lo que se muestra y crea la nueva pantalla"""
        if self._actual is not None:
            self._actual.destroy()
        self._actual = clase(self.area, ventana=self, **kwargs)
        self._actual.pack(fill="both", expand=True)

    def mostrar_inicio(self):
        self.sesion = None
        self.menu.pack_forget()
        self._reemplazar(PantallaInicio)

    def mostrar_acceso(self, rol):
        self._reemplazar(PantallaAcceso, rol=rol)

    def entrar_admin(self):
        self.iniciar_sesion("admin", None, "Administrador")

    def iniciar_sesion(self, rol, identificacion, nombre):
        self.sesion = {"rol": rol, "identificacion": identificacion, "nombre": nombre}
        self._construir_menu()
        self.mostrar_modulo(MENUS[rol][0][0])

    def cerrar_sesion(self):
        self.mostrar_inicio()

    def abrir_perfil(self):
        if not self.sesion:
            return
        perfil = getattr(self, "_ventana_perfil", None)
        if perfil is not None and perfil.winfo_exists():
            perfil.focus_force()
            return
        self._ventana_perfil = VentanaPerfil(self)

    def _hacer_perfil_clicable(self, widget):
        widget.bind(
            "<Button-1>", lambda _evento: self.abrir_perfil(), add="+")
        widget.bind(
            "<Enter>", lambda _evento: self._marcar_perfil_hover(True), add="+")
        widget.bind(
            "<Leave>", lambda _evento: self._marcar_perfil_hover(False), add="+")
        try:
            widget.configure(cursor="hand2")
        except (tk.TclError, ValueError):
            pass
        for hijo in widget.winfo_children():
            self._hacer_perfil_clicable(hijo)

    def _marcar_perfil_hover(self, activo):
        perfil = getattr(self, "_perfil_frame", None)
        if perfil is not None and perfil.winfo_exists():
            perfil.configure(
                fg_color="#244A7F" if activo else COLORES["menu_hover_oscuro"])

    def mostrar_modulo(self, clave):
        rol = self.sesion["rol"]
        clase = next(c for k, _, c in MENUS[rol] if k == clave)
        self._reemplazar(clase)
        for k, boton in self._botones.items():
            activo = k == clave
            boton.configure(
                fg_color=COLORES["acento"] if activo else "transparent",
                hover_color="#E66F10" if activo else COLORES["menu_hover_oscuro"],
                text_color="#FFFFFF" if activo else "#D8E2F0",
                font=("Segoe UI", 12, "bold" if activo else "normal"))

    def _construir_menu(self):
        for hijo in self.menu.winfo_children():
            hijo.destroy()
        self._botones = {}
        rol = self.sesion["rol"]

        self.menu.pack_propagate(False)
        marca = ctk.CTkFrame(self.menu, fg_color="transparent")
        marca.pack(fill="x", padx=20, pady=(24, 20))
        ctk.CTkLabel(
            marca, text="🛵  DOMIYA", text_color="#FFFFFF",
            font=("Segoe UI", 21, "bold")).pack(anchor="w")
        ctk.CTkLabel(
            marca, text="Domicilios en Cali", text_color="#F8A34E",
            font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=(38, 0))

        perfil = ctk.CTkFrame(
            self.menu, fg_color=COLORES["menu_hover_oscuro"], corner_radius=14)
        self._perfil_frame = perfil
        perfil.pack(fill="x", padx=14, pady=(0, 22))
        inicial = (self.sesion["nombre"] or TITULOS_ROL[rol])[0].upper()
        ctk.CTkLabel(
            perfil, text=inicial, width=42, height=42, corner_radius=21,
            fg_color="#F58220", text_color="#FFFFFF",
            font=("Segoe UI", 18, "bold")).pack(
                side="left", padx=12, pady=12)
        detalle = ctk.CTkFrame(perfil, fg_color="transparent")
        detalle.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.lbl_nombre_perfil = ctk.CTkLabel(
            detalle, text=self.sesion["nombre"], text_color="#FFFFFF",
            font=("Segoe UI", 12, "bold"), anchor="w")
        self.lbl_nombre_perfil.pack(fill="x")
        ctk.CTkLabel(
            detalle, text=TITULOS_ROL[rol], text_color="#C7D5E8",
            font=("Segoe UI", 10), anchor="w").pack(fill="x")
        self._hacer_perfil_clicable(perfil)

        navegacion = ctk.CTkScrollableFrame(
            self.menu, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=COLORES["acento"],
            scrollbar_button_hover_color="#D9680B")
        navegacion._scrollbar.configure(width=8, corner_radius=4)
        navegacion.pack(fill="both", expand=True, padx=(4, 0))
        ctk.CTkLabel(
            navegacion, text="MENÚ PRINCIPAL", text_color="#93A9C5",
            font=("Segoe UI", 9, "bold"), anchor="w").pack(
                fill="x", padx=22, pady=(0, 8))

        for clave, texto, _ in MENUS[rol]:
            boton = ctk.CTkButton(
                navegacion, text=f"  {texto}", anchor="w", height=42,
                corner_radius=10, fg_color="transparent",
                hover_color=COLORES["menu_hover_oscuro"],
                text_color="#D8E2F0", font=("Segoe UI", 12),
                command=lambda k=clave: self.mostrar_modulo(k))
            boton.pack(fill="x", padx=12, pady=3)
            self._botones[clave] = boton

        ctk.CTkButton(
            self.menu, text="↪  Cerrar sesión", anchor="w", height=40,
            corner_radius=10, fg_color="transparent",
            hover_color=COLORES["menu_hover_oscuro"], text_color="#D8E2F0",
            font=("Segoe UI", 11), command=self.cerrar_sesion).pack(
                side="bottom", fill="x", padx=12, pady=16)
        self.menu.pack(side="left", fill="y", before=self.area)
