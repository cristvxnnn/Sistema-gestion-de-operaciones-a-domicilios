from tkinter import ttk

COLORES={
    "fondo": "#F4F6FA",
    "tarjeta": "#FFFFFF",
    "borde": "#DDE2EC",
    "texto": "#1F2937",
    "texto_suave": "#6B7280",
    "acento": "#1A56DB",
    "acento_claro": "#E8F0FE",
    "menu_hover": "#F1F5F9",
}
FUENTE = "Segoe UI"
def aplicar_estilos(root):
    """Configura el tema y los estilos nombrados que usan las interfaces."""
    c = COLORES
    s = ttk.Style(root)
    s.theme_use("clam")
    root.configure(background=c["fondo"])

    s.configure("Contenido.TFrame", background=c["fondo"])
    s.configure("Menu.TFrame", background=c["tarjeta"])
    s.configure("Tarjeta.TFrame", background=c["tarjeta"], relief="solid",
                borderwidth=1, bordercolor=c["borde"])

    s.configure("Marca.TLabel", background=c["tarjeta"], foreground=c["acento"],
                font=(FUENTE, 15, "bold"))
    s.configure("MarcaSub.TLabel", background=c["tarjeta"],
                foreground=c["texto_suave"], font=(FUENTE, 9))
    s.configure("Titulo.TLabel", background=c["fondo"], foreground=c["texto"],
                font=(FUENTE, 20, "bold"))
    s.configure("Subtitulo.TLabel", background=c["fondo"],
                foreground=c["texto_suave"], font=(FUENTE, 10))
    s.configure("TarjetaTitulo.TLabel", background=c["tarjeta"],
                foreground=c["texto"], font=(FUENTE, 12, "bold"))
    s.configure("TarjetaTexto.TLabel", background=c["tarjeta"],
                foreground=c["texto_suave"], font=(FUENTE, 9))
    s.configure("Estado.TLabel", background=c["tarjeta"],
                foreground=c["texto_suave"], font=(FUENTE, 9))

    # Botones del menú lateral
    s.configure("Menu.TButton", background=c["tarjeta"], foreground=c["texto"],
                font=(FUENTE, 11), anchor="w", padding=(18, 10),
                borderwidth=0, relief="flat", focuscolor=c["tarjeta"])
    s.map("Menu.TButton", background=[("active", c["menu_hover"])])
    s.configure("MenuActivo.TButton", background=c["acento_claro"],
                foreground=c["acento"], font=(FUENTE, 11, "bold"), anchor="w",
                padding=(18, 10), borderwidth=0, relief="flat",
                focuscolor=c["acento_claro"])
    s.map("MenuActivo.TButton", background=[("active", c["acento_claro"])])

    # Botón de acción principal
    s.configure("Accion.TButton", background=c["acento"], foreground="#FFFFFF",
                font=(FUENTE, 10, "bold"), padding=(14, 6), borderwidth=0)
    s.map("Accion.TButton", background=[("active", "#1647B8")])

    # Tablas
    s.configure("Treeview", background=c["tarjeta"], fieldbackground=c["tarjeta"],
                foreground=c["texto"], rowheight=28, font=(FUENTE, 10))
    s.configure("Treeview.Heading", background=c["acento_claro"],
                foreground=c["acento"], font=(FUENTE, 10, "bold"))
