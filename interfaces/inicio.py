import sys
import tkinter as tk
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageOps, ImageTk

from interfaces.estilos import COLORES


def _ruta_recurso(nombre):
    """Encuentra recursos tanto al ejecutar Python como dentro del .exe."""
    raiz = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return raiz / "imagenes" / nombre


class PantallaInicio(ctk.CTkFrame):
    """Portada de EntreCali con ilustración y acceso por perfil."""

    def __init__(self, parent, ventana=None):
        super().__init__(parent, fg_color="#F3F6FC", corner_radius=0)
        self.ventana = ventana
        self._escena_original = self._abrir_imagen("assets_inicio/portada_escena.png")
        self._logo = None
        self._imagen_escena = None
        self._iconos_perfil = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        cabecera = ctk.CTkFrame(self, fg_color="transparent", height=76)
        cabecera.grid(row=0, column=0, sticky="ew", padx=28, pady=(10, 5))
        cabecera.grid_columnconfigure(0, weight=1)
        logo = self._abrir_imagen("assets_inicio/portada_logo.png")
        if logo:
            self._logo = ctk.CTkImage(
                light_image=logo, dark_image=logo, size=(238, 75))
            ctk.CTkLabel(cabecera, text="", image=self._logo).grid(
                row=0, column=0, sticky="w")
        else:
            ctk.CTkLabel(
                cabecera, text="ENTRECALI", text_color=COLORES["texto"],
                font=("Segoe UI", 24, "bold")).grid(row=0, column=0, sticky="w")

        estado_ciudad = ctk.CTkFrame(
            cabecera, fg_color="#FFFFFF", corner_radius=22,
            border_width=1, border_color="#DCE6F3")
        estado_ciudad.grid(row=0, column=1, sticky="e", padx=(0, 4))
        ctk.CTkLabel(
            estado_ciudad, text="Domicilios en Cali", text_color="#354C70",
            font=("Segoe UI", 11)).pack(side="left", padx=14, pady=8)

        contenido = ctk.CTkFrame(self, fg_color="transparent")
        contenido.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 8))
        contenido.grid_columnconfigure(0, weight=49, uniform="paneles")
        contenido.grid_columnconfigure(1, weight=51, uniform="paneles")
        contenido.grid_rowconfigure(0, weight=1)

        visual = ctk.CTkFrame(contenido, fg_color="transparent", corner_radius=0)
        visual.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        visual.grid_columnconfigure(0, weight=1)
        visual.grid_rowconfigure(4, weight=1)

        linea_1 = ctk.CTkFrame(visual, fg_color="transparent")
        linea_1.grid(row=0, column=0, sticky="ew", padx=(16, 8), pady=(22, 0))

        ctk.CTkLabel(
            linea_1, text="Lo pides en ", text_color="#122B50",
            font=("Segoe UI", 30, "bold")
        ).pack(side="left")

        ctk.CTkLabel(
            linea_1, text="segundos,", text_color="#F58220",
            font=("Segoe UI", 30, "bold")
        ).pack(side="left")

        linea_2 = ctk.CTkFrame(visual, fg_color="transparent")
        linea_2.grid(row=1, column=0, sticky="ew", padx=(16, 8), pady=0)

        ctk.CTkLabel(
            linea_2, text="      lo tienes en ", text_color="#122B50",
            font=("Segoe UI", 31, "bold")
        ).pack(side="left")

        ctk.CTkLabel(
            linea_2, text="minutos", text_color="#F58220",
            font=("Segoe UI", 31, "bold")
        ).pack(side="left")

        ctk.CTkFrame(
            visual, fg_color=COLORES["acento"], corner_radius=3, height=4,
            width=110).grid(row=2, column=0, sticky="w", padx=(250, 0), pady=(0, 1))
        ctk.CTkLabel(
            visual, text="\nTodo lo que necesitas\n hasta la puerta de tu casa.",
            text_color="#526789", font=("Segoe UI", 13), anchor="w",
            justify="left").grid(row=3, column=0, sticky="ew",
                                 padx=(18, 8), pady=(5, 0))

        escena = ctk.CTkFrame(visual, fg_color="transparent", corner_radius=0)
        escena.grid(row=4, column=0, sticky="nsew", padx=(0, 0), pady=(0, 0))
        escena.grid_columnconfigure(0, weight=1)
        escena.grid_rowconfigure(0, weight=1)
        self._lbl_escena = tk.Label(
            escena, borderwidth=0, highlightthickness=0,
            background="#F3F6FC", anchor="center")
        self._lbl_escena.grid(row=0, column=0, sticky="nsew")
        self._lbl_escena.bind("<Configure>", self._ajustar_escena, add="+")

        acceso = ctk.CTkFrame(
            contenido, fg_color="#FFFFFF", corner_radius=24,
            border_width=1, border_color="#E1E8F3")
        acceso.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        acceso.grid_columnconfigure(0, weight=1)
        acceso.grid_rowconfigure(0, weight=1)
        acceso.grid_rowconfigure(7, weight=1)
        ctk.CTkLabel(
            acceso, text="¡Bienvenido!", text_color="#122B50",
            font=("Segoe UI", 29, "bold"), anchor="w").grid(
                row=1, column=0, sticky="ew", padx=30, pady=(18, 1))
        ctk.CTkLabel(
            acceso, text="Selecciona tu perfil para continuar.",
            text_color="#526789", font=("Segoe UI", 13), anchor="w").grid(
                row=2, column=0, sticky="ew", padx=30, pady=(0, 0))
        ctk.CTkFrame(
            acceso, fg_color=COLORES["acento"], corner_radius=3,
            width=104, height=5).grid(row=3, column=0, sticky="w",
                                      padx=30, pady=(14, 18))

        opciones = [
            ("perfil_cliente.png", "Cliente",
             "Realiza pedidos y consulta tus compras.",
             lambda: ventana.mostrar_acceso("cliente")),
            ("perfil_domiciliario.png", "Domiciliario",
             "Gestiona entregas y actualiza pedidos.",
             lambda: ventana.mostrar_acceso("domiciliario")),
            ("perfil_admin.png", "Administrador",
             "Controla la operación del sistema.",
             ventana.entrar_admin),
        ]
        for fila, (archivo_icono, titulo, descripcion, accion) in enumerate(opciones, start=4):
            tarjeta = ctk.CTkFrame(
                acceso, fg_color="#FFFFFF", corner_radius=17,
                border_width=1, border_color="#E0E7F2")
            tarjeta.grid(row=fila, column=0, sticky="ew", padx=20, pady=7)
            tarjeta.grid_columnconfigure(1, weight=1)
            icono = self._abrir_imagen(f"assets_inicio/{archivo_icono}")
            if icono:
                imagen_icono = ctk.CTkImage(
                    light_image=icono, dark_image=icono, size=(70, 70))
                self._iconos_perfil.append(imagen_icono)
                ctk.CTkLabel(tarjeta, text="", image=imagen_icono).grid(
                    row=0, column=0, padx=(11, 12), pady=11)
            textos = ctk.CTkFrame(tarjeta, fg_color="transparent")
            textos.grid(row=0, column=1, sticky="ew", pady=12)
            ctk.CTkLabel(
                textos, text=titulo, text_color="#122B50",
                font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(
                textos, text=descripcion, text_color="#526789",
                font=("Segoe UI", 10), anchor="w", wraplength=240,
                justify="left").pack(fill="x", pady=(2, 0))
            ctk.CTkButton(
                tarjeta, text="Entrar  ›", width=104, height=44,
                corner_radius=13, fg_color=COLORES["acento"], hover_color="#E66F10",
                font=("Segoe UI", 12, "bold"), command=accion).grid(
                    row=0, column=2, padx=12, pady=12)

        self.after_idle(self._ajustar_escena)

    @staticmethod
    def _abrir_imagen(nombre):
        try:
            return Image.open(_ruta_recurso(nombre)).convert("RGBA")
        except (OSError, ValueError):
            return None

    def _ajustar_escena(self, _evento=None):
        if self._escena_original is None or not self.winfo_exists():
            return
        ancho = self._lbl_escena.winfo_width()
        alto = self._lbl_escena.winfo_height()
        if ancho < 2 or alto < 2:
            return
        escena = ImageOps.contain(
            self._escena_original, (ancho, alto),
            method=Image.Resampling.LANCZOS)
        self._imagen_escena = ImageTk.PhotoImage(escena)
        self._lbl_escena.configure(image=self._imagen_escena)
