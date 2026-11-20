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
        {
            "nombre": "Pan tajado",
            "precio": 6200,
            "imagen": "https://placehold.co/160x100/png?text=Pan",
        },
        {
            "nombre": "Queso tajado",
            "precio": 11500,
            "imagen": "https://placehold.co/160x100/png?text=Queso",
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
        {
            "nombre": "Suero oral",
            "precio": 9500,
            "imagen": "https://placehold.co/160x100/png?text=Suero",
        },
        {
            "nombre": "Ibuprofeno",
            "precio": 7200,
            "imagen": "https://placehold.co/160x100/png?text=Ibuprofeno",
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
        {
            "nombre": "Helado",
            "precio": 11000,
            "imagen": "https://placehold.co/160x100/png?text=Helado",
        },
        {
            "nombre": "Pita griega",
            "precio": 24000,
            "imagen": "https://placehold.co/160x100/png?text=Pita",
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
        {
            "nombre": "Protector solar",
            "precio": 32000,
            "imagen": "https://placehold.co/160x100/png?text=Protector",
        },
        {
            "nombre": "Gel antibacterial",
            "precio": 7000,
            "imagen": "https://placehold.co/160x100/png?text=Gel",
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
        {
            "nombre": "Frisby snacks",
            "precio": 16500,
            "imagen": "https://placehold.co/160x100/png?text=Snacks",
        },
        {
            "nombre": "Ensalada coleslaw",
            "precio": 6500,
            "imagen": "https://placehold.co/160x100/png?text=Ensalada",
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
        {
            "nombre": "Frijol",
            "precio": 7800,
            "imagen": "https://placehold.co/160x100/png?text=Frijol",
        },
        {
            "nombre": "Café molido",
            "precio": 13500,
            "imagen": "https://placehold.co/160x100/png?text=Cafe",
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
        {
            "nombre": "Jabón líquido",
            "precio": 11000,
            "imagen": "https://placehold.co/160x100/png?text=Jabon",
        },
        {
            "nombre": "Limpiavidrios",
            "precio": 6800,
            "imagen": "https://placehold.co/160x100/png?text=Limpiador",
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
        {
            "nombre": "Cinta embalaje",
            "precio": 4500,
            "imagen": "https://placehold.co/160x100/png?text=Cinta",
        },
        {
            "nombre": "Plástico burbuja",
            "precio": 6000,
            "imagen": "https://placehold.co/160x100/png?text=Burbuja",
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
        {
            "nombre": "Bolsa mensajería",
            "precio": 2500,
            "imagen": "https://placehold.co/160x100/png?text=Bolsa",
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
        {
            "nombre": "Kit belleza",
            "precio": 32000,
            "imagen": "https://placehold.co/160x100/png?text=Kit+4",
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
