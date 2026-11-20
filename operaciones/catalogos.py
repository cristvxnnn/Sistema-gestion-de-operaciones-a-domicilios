"""Catálogo inicial de productos para las solicitudes.

Es un catálogo de demostración. Sus claves están preparadas para migrarse
posteriormente a una tabla producto y a una tabla detalleSolicitud.
"""
import unicodedata

CATALOGO_PRODUCTOS = {
    "Carulla": [
        {
            "nombre": "Arroz",
            "precio": 5000,
            "imagen": "https://placehold.co/160x100/png?text=Arroz",
        },
        {
            "nombre": "Huevos",
            "precio": 18000,
            "imagen": "https://placehold.co/160x100/png?text=Huevos",
        },
        {
            "nombre": "Leche",
            "precio": 4500,
            "imagen": "https://placehold.co/160x100/png?text=Leche",
        },
    ],
    "Cruz Verde": [
        {
            "nombre": "Acetaminofén",
            "precio": 8000,
            "imagen": "https://placehold.co/160x100/png?text=Acetaminofen",
        },
        {
            "nombre": "Alcohol antiséptico",
            "precio": 6500,
            "imagen": "https://placehold.co/160x100/png?text=Alcohol",
        },
        {
            "nombre": "Gasas estériles",
            "precio": 5500,
            "imagen": "https://placehold.co/160x100/png?text=Gasas",
        },
    ],
    "Crepes & Waffles": [
        {
            "nombre": "Crepe de pollo",
            "precio": 26000,
            "imagen": "https://placehold.co/160x100/png?text=Crepe",
        },
        {
            "nombre": "Waffle",
            "precio": 18000,
            "imagen": "https://placehold.co/160x100/png?text=Waffle",
        },
        {
            "nombre": "Limonada",
            "precio": 9000,
            "imagen": "https://placehold.co/160x100/png?text=Limonada",
        },
    ],
    "Farmatodo": [
        {
            "nombre": "Acetaminofén",
            "precio": 7500,
            "imagen": "https://placehold.co/160x100/png?text=Acetaminofen",
        },
        {
            "nombre": "Vitamina C",
            "precio": 12000,
            "imagen": "https://placehold.co/160x100/png?text=Vitamina+C",
        },
        {
            "nombre": "Curitas",
            "precio": 6000,
            "imagen": "https://placehold.co/160x100/png?text=Curitas",
        },
    ],
    "Frisby": [
        {
            "nombre": "Pollo personal",
            "precio": 22000,
            "imagen": "https://placehold.co/160x100/png?text=Pollo",
        },
        {
            "nombre": "Papas fritas",
            "precio": 8000,
            "imagen": "https://placehold.co/160x100/png?text=Papas",
        },
        {
            "nombre": "Gaseosa",
            "precio": 5000,
            "imagen": "https://placehold.co/160x100/png?text=Gaseosa",
        },
    ],
    "Surtifamiliar": [
        {
            "nombre": "Arroz",
            "precio": 5000,
            "imagen": "https://placehold.co/160x100/png?text=Arroz",
        },
        {
            "nombre": "Aceite",
            "precio": 9000,
            "imagen": "https://placehold.co/160x100/png?text=Aceite",
        },
        {
            "nombre": "Azúcar",
            "precio": 4500,
            "imagen": "https://placehold.co/160x100/png?text=Azucar",
        },
    ],
    "Droquímicos Cali": [
        {
            "nombre": "Detergente",
            "precio": 10000,
            "imagen": "https://placehold.co/160x100/png?text=Detergente",
        },
        {
            "nombre": "Desinfectante",
            "precio": 8500,
            "imagen": "https://placehold.co/160x100/png?text=Desinfectante",
        },
        {
            "nombre": "Guantes",
            "precio": 7000,
            "imagen": "https://placehold.co/160x100/png?text=Guantes",
        },
    ],
    "Inter Rapidísimo S.A.": [
        {
            "nombre": "Envío nacional",
            "precio": 18000,
            "imagen": "https://placehold.co/160x100/png?text=Envio",
        },
        {
            "nombre": "Caja pequeña",
            "precio": 7000,
            "imagen": "https://placehold.co/160x100/png?text=Caja",
        },
        {
            "nombre": "Sobre manila",
            "precio": 3000,
            "imagen": "https://placehold.co/160x100/png?text=Sobre",
        },
    ],
    "Servientrega": [
        {
            "nombre": "Guía urbana",
            "precio": 16000,
            "imagen": "https://placehold.co/160x100/png?text=Guia",
        },
        {
            "nombre": "Caja mediana",
            "precio": 9000,
            "imagen": "https://placehold.co/160x100/png?text=Caja",
        },
        {
            "nombre": "Sobre de seguridad",
            "precio": 3500,
            "imagen": "https://placehold.co/160x100/png?text=Sobre",
        },
    ],
    "Krika": [
        {
            "nombre": "Producto básico",
            "precio": 15000,
            "imagen": "https://placehold.co/160x100/png?text=Producto+1",
        },
        {
            "nombre": "Producto estándar",
            "precio": 25000,
            "imagen": "https://placehold.co/160x100/png?text=Producto+2",
        },
        {
            "nombre": "Producto premium",
            "precio": 40000,
            "imagen": "https://placehold.co/160x100/png?text=Producto+3",
        },
    ],
}


def _normalizar_nombre(nombre):
    texto = unicodedata.normalize("NFKD", nombre or "")
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    return " ".join(texto.casefold().split())


def catalogo_para_establecimiento(nombre):
    """Busca productos sin depender de mayúsculas o espacios accidentales."""
    buscado = _normalizar_nombre(nombre)
    for establecimiento, productos in CATALOGO_PRODUCTOS.items():
        if _normalizar_nombre(establecimiento) == buscado:
            return productos
    # Algunos datos antiguos pueden aparecer con un carácter de reemplazo
    # por una codificación previa de la base de datos.
    if "droqu" in buscado and "cali" in buscado:
        return CATALOGO_PRODUCTOS["Droquímicos Cali"]
    if "rapid" in buscado and "simo" in buscado:
        return CATALOGO_PRODUCTOS["Inter Rapidísimo S.A."]
    return []
