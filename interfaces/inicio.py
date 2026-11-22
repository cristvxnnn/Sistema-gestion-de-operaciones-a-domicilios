import os
import sys
import tkinter as tk
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageTk

from interfaces.estilos import COLORES


def _ruta_recurso(nombre):
    """Encuentra recursos tanto al ejecutar Python como dentro del .exe."""
    raiz = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return raiz / "imagenes" / nombre


class PantallaInicio(ctk.CTkFrame):
    def __init__(self, parent, ventana=None):
        super().__init__(parent, fg_color=COLORES["fondo"], corner_radius=0)
        self.ventana = ventana

        hero = ctk.CTkFrame(
            self, fg_color=COLORES["menu"], corner_radius=24)
        hero.pack(side="left", fill="both", expand=True, padx=(28, 14), pady=28)
        hero.columnconfigure(0, weight=1)

        try:
            self._foto_original = Image.open(
                _ruta_recurso("entrecali_fondo.jpg")).convert("RGB")
            self._fondo = tk.Label(
                hero, borderwidth=0, highlightthickness=0,
                background=COLORES["menu"])
            self._fondo.place(x=0, y=0, relwidth=1, relheight=1)
            hero.bind("<Configure>", self._ajustar_fondo, add="+")
            self.after_idle(self._ajustar_fondo)
        except (OSError, ValueError):
            self._foto_original = None
            self._imagen_fondo = None

        try:
            logo = Image.open(_ruta_recurso("entrecali_logo.png")).convert("RGBA")
            self._imagen_logo = ctk.CTkImage(
                light_image=logo, dark_image=logo, size=(390, 69))
            tarjeta_logo = ctk.CTkFrame(
                hero, fg_color="#FFFFFF", corner_radius=14)
            tarjeta_logo.pack(anchor="w", padx=38, pady=(48, 0))
            ctk.CTkLabel(
                tarjeta_logo, text="", image=self._imagen_logo,
                fg_color="#FFFFFF").pack(padx=15, pady=10)
        except (OSError, ValueError):
            self._imagen_logo = None
            ctk.CTkLabel(
                hero, text="EntreCali", text_color="#FFFFFF",
                fg_color="transparent", font=("Segoe UI", 38, "bold")).pack(
                    anchor="w", padx=48, pady=(58, 10))

        acceso = ctk.CTkFrame(self, fg_color="transparent", width=420)
        acceso.pack(side="right", fill="y", padx=(14, 28), pady=28)
        acceso.pack_propagate(False)
        ctk.CTkLabel(
            acceso, text="Bienvenido", text_color=COLORES["texto"],
            font=("Segoe UI", 28, "bold")).pack(anchor="w", pady=(68, 5))
        ctk.CTkLabel(
            acceso, text="Elige cómo quieres ingresar al sistema.",
            text_color=COLORES["texto_suave"], font=("Segoe UI", 13),
            wraplength=370, justify="left").pack(anchor="w", pady=(0, 26))

        opciones = [
            ("🛍️", "Cliente", "Crea solicitudes y consulta tus pedidos.",
             lambda: ventana.mostrar_acceso("cliente")),
            ("🛵", "Domiciliario", "Gestiona entregas y reporta incidentes.",
             lambda: ventana.mostrar_acceso("domiciliario")),
            ("⚙️", "Administrador", "Consulta la operación del sistema.",
             ventana.entrar_admin),
        ]
        for icono, titulo, descripcion, accion in opciones:
            tarjeta = ctk.CTkFrame(
                acceso, fg_color=COLORES["tarjeta"], corner_radius=16,
                border_width=1, border_color=COLORES["borde"])
            tarjeta.pack(fill="x", pady=7)
            ctk.CTkLabel(
                tarjeta, text=icono, width=44, height=44, corner_radius=12,
                fg_color=COLORES["acento_claro"],
                font=("Segoe UI Emoji", 20)).pack(
                    side="left", padx=14, pady=14)
            texto = ctk.CTkFrame(tarjeta, fg_color="transparent")
            texto.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=12)
            ctk.CTkLabel(
                texto, text=titulo, text_color=COLORES["texto"],
                font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(
                texto, text=descripcion, text_color=COLORES["texto_suave"],
                font=("Segoe UI", 10), anchor="w", wraplength=260,
                justify="left").pack(fill="x", pady=(2, 0))
            ctk.CTkButton(
                tarjeta, text="Entrar", width=76, height=34, corner_radius=9,
                fg_color=COLORES["acento"], hover_color="#E66F10",
                font=("Segoe UI", 11, "bold"), command=accion).pack(
                    side="right", padx=14, pady=14)

    def _ajustar_fondo(self, _evento=None):
        if self._foto_original is None or not self.winfo_exists():
            return
        ancho = max(self._fondo.winfo_width(), 1)
        alto = max(self._fondo.winfo_height(), 1)
        if ancho < 2 or alto < 2:
            return
        foto = ImageOps.fit(
            self._foto_original, (ancho, alto),
            method=Image.Resampling.LANCZOS, centering=(0.5, 0.5)).convert("RGBA")
        escala = alto / 730
        ruta_fuentes = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
        try:
            titulo = ImageFont.truetype(str(ruta_fuentes / "segoeuib.ttf"), max(18, int(27 * escala)))
            cuerpo = ImageFont.truetype(str(ruta_fuentes / "segoeui.ttf"), max(12, int(15 * escala)))
            detalle = ImageFont.truetype(str(ruta_fuentes / "segoeuib.ttf"), max(11, int(12 * escala)))
            pie = ImageFont.truetype(str(ruta_fuentes / "segoeui.ttf"), max(9, int(10 * escala)))
        except OSError:
            titulo = cuerpo = detalle = pie = ImageFont.load_default()
        dibujo = ImageDraw.Draw(foto)
        x = int(50 * escala)
        sombra = (12, 29, 55, 180)
        dibujo.text((x, int(190 * escala)), "Cali se mueve contigo",
                    font=titulo, fill="#FFFFFF", stroke_width=1, stroke_fill=sombra)
        dibujo.text((x + 2, int(237 * escala)),
                    "Comercios, pedidos y domicilios en un mismo lugar.",
                    font=cuerpo, fill="#F2F6FC", stroke_width=1, stroke_fill=sombra)
        dibujo.text((x + 2, int(280 * escala)),
                    "Rápido  ·  Cercano  ·  Hecho para Cali",
                    font=detalle, fill="#FFD09C", stroke_width=1, stroke_fill=sombra)
        dibujo.text((int(32 * escala), alto - int(39 * escala)),
                    "Santiago de Cali  ·  Colombia", font=pie,
                    fill="#F2F6FC", stroke_width=1, stroke_fill=sombra)
        mascara = Image.new("L", (ancho, alto), 0)
        ImageDraw.Draw(mascara).rounded_rectangle(
            (0, 0, ancho - 1, alto - 1), radius=24, fill=255)
        foto.putalpha(mascara)
        self._imagen_fondo = ImageTk.PhotoImage(foto)
        self._fondo.configure(image=self._imagen_fondo)
