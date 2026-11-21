import customtkinter as ctk

from interfaces.estilos import COLORES


class PantallaInicio(ctk.CTkFrame):
    def __init__(self, parent, ventana=None):
        super().__init__(parent, fg_color=COLORES["fondo"], corner_radius=0)
        self.ventana = ventana

        hero = ctk.CTkFrame(
            self, fg_color=COLORES["menu"], corner_radius=24)
        hero.pack(side="left", fill="both", expand=True, padx=(28, 14), pady=28)
        hero.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hero, text="🛵", font=("Segoe UI Emoji", 74),
            text_color="#F58220").pack(anchor="w", padx=48, pady=(58, 10))
        ctk.CTkLabel(
            hero, text="DOMIYA", text_color="#FFFFFF",
            font=("Segoe UI", 40, "bold")).pack(anchor="w", padx=48)
        ctk.CTkLabel(
            hero, text="Domicilios en Cali", text_color="#F8A34E",
            font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=50, pady=(0, 22))
        ctk.CTkLabel(
            hero, text="Rápido  •  Seguro  •  Confiable",
            text_color="#D8E2F0", font=("Segoe UI", 15)).pack(
                anchor="w", padx=50)
        ctk.CTkLabel(
            hero, text="Conectamos a Cali con lo que necesitas.",
            text_color="#AFC1D8", font=("Segoe UI", 12)).pack(
                anchor="w", padx=50, pady=(8, 0))
        ctk.CTkLabel(
            hero, text="Santiago de Cali  ·  Colombia",
            text_color="#93A9C5", font=("Segoe UI", 10)).pack(
                side="bottom", anchor="w", padx=32, pady=24)

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
