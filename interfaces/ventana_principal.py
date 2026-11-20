import tkinter as tk
from tkinter import ttk, messagebox

from database.conexion import probar_conexion
from interfaces.estilos import aplicar_estilos, COLORES
from interfaces.inicio import PantallaInicio
from interfaces.acceso import PantallaAcceso
from interfaces.menus import MENUS, TITULOS_ROL


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de gestión de domicilios")
        self.geometry("1100x680")
        self.minsize(960, 600)
        aplicar_estilos(self)

        self.sesion = None          # {"rol", "identificacion", "nombre"} o None
        self._actual = None         # widget que se está mostrando
        self._botones = {}          # clave de módulo -> botón del menú

        self._crear_barra_estado()
        self.menu = ttk.Frame(self, style="Menu.TFrame", width=240)
        self.area = ttk.Frame(self, style="Contenido.TFrame")
        self.area.pack(side="left", fill="both", expand=True)

        self.mostrar_inicio()
        self.after(150, self._verificar_conexion)

    def _crear_barra_estado(self):
        barra = ttk.Frame(self, style="Menu.TFrame")
        barra.pack(side="bottom", fill="x")
        self.lbl_conexion = ttk.Label(barra, text="Base de datos: sin conexión",
                                      style="Estado.TLabel")
        self.lbl_conexion.pack(side="left", padx=12, pady=4)

    def actualizar_estado_conexion(self, texto):
        self.lbl_conexion.configure(text=texto)

    def _verificar_conexion(self):
        ok, mensaje = probar_conexion()
        if ok:
            self.actualizar_estado_conexion(f"Base de datos: conectado — {mensaje}")
        else:
            self.actualizar_estado_conexion("Base de datos: sin conexión")
            messagebox.showwarning("Sin conexión", mensaje)

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

    def mostrar_modulo(self, clave):
        rol = self.sesion["rol"]
        clase = next(c for k, _, c in MENUS[rol] if k == clave)
        self._reemplazar(clase)
        for k, boton in self._botones.items():
            boton.configure(style="MenuActivo.TButton" if k == clave else "Menu.TButton")

    def _construir_menu(self):
        for hijo in self.menu.winfo_children():
            hijo.destroy()
        self._botones = {}
        rol = self.sesion["rol"]

        tk.Frame(self.menu, width=1, background=COLORES["borde"]).pack(side="right", fill="y")
        ttk.Label(self.menu, text="Domicilios", style="Marca.TLabel").pack(
            anchor="w", padx=18, pady=(22, 0))
        ttk.Label(self.menu, text=TITULOS_ROL[rol], style="MarcaSub.TLabel").pack(
            anchor="w", padx=18)
        if rol != "admin":
            ttk.Label(self.menu, text=f"Hola, {self.sesion['nombre']}",
                      style="TarjetaTitulo.TLabel").pack(anchor="w", padx=18, pady=(10, 0))
        ttk.Frame(self.menu, style="Menu.TFrame", height=18).pack()

        for clave, texto, _ in MENUS[rol]:
            boton = ttk.Button(self.menu, text=texto, style="Menu.TButton",
                               command=lambda k=clave: self.mostrar_modulo(k))
            boton.pack(fill="x")
            self._botones[clave] = boton

        ttk.Button(self.menu, text="Cerrar sesión", style="Secundario.TButton",
                   command=self.cerrar_sesion).pack(side="bottom", padx=18, pady=18, anchor="w")

        self.menu.pack_propagate(False)
        self.menu.pack(side="left", fill="y", before=self.area)
