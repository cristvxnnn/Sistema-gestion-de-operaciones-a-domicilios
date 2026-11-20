from tkinter import ttk


class PantallaInicio(ttk.Frame):
    def __init__(self, parent, ventana=None):
        super().__init__(parent, style="Contenido.TFrame")
        self.ventana = ventana

        centro = ttk.Frame(self, style="Contenido.TFrame")
        centro.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(centro, text="Sistema de gestión de domicilios",
                  style="Titulo.TLabel").pack()
        ttk.Label(centro, text="¿cómo quieres ingresar?",
                  style="Subtitulo.TLabel").pack(pady=(4, 26))

        fila = ttk.Frame(centro, style="Contenido.TFrame")
        fila.pack()

        opciones = [
            ("Soy cliente", "Pide domicilios y consulta el estado de tus solicitudes.",
             "Ingresar como cliente", lambda: ventana.mostrar_acceso("cliente")),
            ("Soy domiciliario", "Toma solicitudes, actualiza su estado y reporta incidentes.",
             "Ingresar como domiciliario", lambda: ventana.mostrar_acceso("domiciliario")),
            ("Administrador", "Dashboard general, solicitudes y consultas del sistema.",
             "Abrir panel", ventana.entrar_admin),
        ]
        for titulo, texto, boton, accion in opciones:
            tarjeta = ttk.Frame(fila, style="Tarjeta.TFrame", padding=22)
            tarjeta.pack(side="left", padx=10, fill="y")
            ttk.Label(tarjeta, text=titulo, style="TarjetaTitulo.TLabel").pack(anchor="w")
            ttk.Label(tarjeta, text=texto, style="TarjetaTexto.TLabel",
                      wraplength=190, justify="left").pack(anchor="w", pady=(6, 16))
            ttk.Button(tarjeta, text=boton, style="Accion.TButton",
                       command=accion).pack(anchor="w", side="bottom")