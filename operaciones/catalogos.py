"""Catálogo inicial de productos para las solicitudes.

Es un catálogo de demostración. Sus claves están preparadas para migrarse
posteriormente a una tabla producto y a una tabla detalleSolicitud.
"""
from pathlib import Path
import unicodedata


IMAGENES_DIR = Path(__file__).resolve().parent.parent / "imagenes"

IMAGENES_ESTABLECIMIENTOS = {
    "Carulla": "carulla.png",
    "Cruz Verde": "cruz_verde.png",
    "Crepes & Waffles": "crepes_waffles.png",
    "Farmatodo": "farmatodo.png",
    "Frisby": "frisby.png",
    "Surtifamiliar": "surtifamiliar.png",
    "Droquímicos Cali": "droquimicos_cali.png",
    "Inter Rapidísimo S.A.": "inter_rapidisimo.png",
    "Servientrega": "servientrega.png",
    "Krika": "krika.png",
}

# Archivos entregados en la carpeta imagenes. Un mismo producto puede aparecer
# en más de un establecimiento y reutilizar la misma imagen local.
IMAGENES_LOCALES = {
    "Arroz": "Arroz-Blanco-CARULLA-1000-gr-3181783_a.jpg",
    "Huevos": "HUEVO-ROJO-X-30-AAA-1513316_a.jpg",
    "Leche": "Leche-Entera-UHT-CARULLA-1100-ml-3374934_a.jpg",
    "Pan tajado": "Pan-Tajado-Blanco-CARULLA-600-gr-3317922_a.jpg",
    "Queso tajado": "Queso-Mozzarella-Tajado-CARULLA-400-gr-3298215_a.jpg",
    "Acetaminofén": "waffle.jpg.jpeg",
    "Alcohol antiséptico": "Alcohol-Antiseptico-OSA-700ml-1-1024x1024.jpg.jpeg",
    "Gasas estériles": "gasas.jpg.jpeg",
    "Suero oral": "suero_oral.jpg.jpeg",
    "Ibuprofeno": "ibuprofeno.jpg.jpeg",
    "Crepe de pollo": "crepe_pollo.jpg.jpeg",
    "Waffle": "pexels-rodrigo-kokama-538969654-18857730.jpg.jpeg",
    "Limonada": "Limonada.jpg",
    "Helado": "helado.jpg",
    "Pita griega": "pitagriega.jpg",
    "Vitamina C": "vitamina_c.jpg.jpeg",
    "Curitas": "curitas.jpg.jpeg",
    "Protector solar": "protector_solar.jpg.jpeg",
    "Gel antibacterial": "gel_antibacterial.jpg.jpeg",
    "Pollo personal": "PolloPersonal.jpg",
    "Papas fritas": "papasFritas.jpg",
    "Gaseosa": "Gaseosa-Colombiana-x-400-ml-1058142_a.jpg",
    "Frisby snacks": "firsbysnacks.jpg",
    "Ensalada coleslaw": "Ensalada coleslaw.jpg",
    "Aceite": "Aceites-Aceites-Liquidos-ACESURTIFAMILIAR-x500ml-SOYA-552420201112135902.webp",
    "Azúcar": "Granos-Empacados-Granos-Empacados-AZUCPROVIDENCIA-x2500g-BCA-5620201112095402SURTIFAMILIAR.webp",
    "Frijol": "FrijolSurtifamiliar.jpg",
    "Café molido": "20240502082646-Cafe-Cafe-Molido-Cafe-Surtifamiliar-x500g-Molido-2241202405020826463689.webp",
    "Detergente": "detergente.jpg",
    "Desinfectante": "limpiador-desinfectante-x3785.jpg",
    "Guantes": "guantes.jpg",
    "Jabón líquido": "jabon-liquido-antibact-avena-coco-1000ml-12006237-01.png.png",
    "Limpiavidrios": "limpiavidrios.webp",
    "Envío nacional": "envioNacional.jpg",
    "Caja pequeña": "cajaPequeñaInter.jpg",
    "Sobre manila": "sobreManila.jpg",
    "Cinta embalaje": "CintaDeEmbalaje.jpg",
    "Plástico burbuja": "plastico burbuja inter rapidisimo.jpg",
    "Envío confidencial": "guía urbana servientrega.jpg",
    "Caja mediana": "Caja mediana servientrega.png",
    "Sobre de seguridad": "SobreDe seguridad servientrega.webp",
    "Bolsa mensajería": "Bolsa de mensajeria servientrega.jpg",
    "Wella Fusion Reparación Intensiva 250 ml": (
        "Wella Shampoo Fusion Reparación Intensiva.jpg"
    ),
    "Recamier Vegan Keratin Salon In 1000 ml": (
        "Recamier Shampoo Salon In Vegan Keratin — 1000 ml.jpg"
    ),
    "Recamier Liss Control Salon In 1000 ml": (
        "Recamier Shampoo Salon In Liss Control — 1000 ml .jpg"
    ),
    "Lehit Ampolleta Ácido Hialurónico 15 ml": (
        "Lehit Ampolleta Ácido Hialurónico — 15 ml.png"
    ),
    "Ana María Limpiador Equilibrante": (
        "Ana María Limpiador Equilibrante.jpg"
    ),
}

# Permite usar la imagen específica de Arroz de Surtifamiliar sin perder la
# imagen de Arroz de Carulla.
IMAGENES_POR_ESTABLECIMIENTO = {
    ("Surtifamiliar", "Arroz"): (
        "20260623105835-Granos-Empacados-Granos-Empacados-Arroz-"
        "Surtifamiliar-X2500g-303202606231058356791.webp"
    ),
}

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
            "nombre": "Envío confidencial",
            "precio": 50000,
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
            "nombre": "Wella Fusion Reparación Intensiva 250 ml",
            "precio": 113400,
            "imagen": "https://placehold.co/160x100/png?text=Wella",
        },
        {
            "nombre": "Recamier Vegan Keratin Salon In 1000 ml",
            "precio": 36000,
            "imagen": "https://placehold.co/160x100/png?text=Recamier",
        },
        {
            "nombre": "Recamier Liss Control Salon In 1000 ml",
            "precio": 67428,
            "imagen": "https://placehold.co/160x100/png?text=Recamier",
        },
        {
            "nombre": "Lehit Ampolleta Ácido Hialurónico 15 ml",
            "precio": 8900,
            "imagen": "https://placehold.co/160x100/png?text=Lehit",
        },
        {
            "nombre": "Ana María Limpiador Equilibrante",
            "precio": 28700,
            "imagen": "https://placehold.co/160x100/png?text=Ana+Maria",
        },
    ],
}


def _imagen_local(nombre_archivo):
    """Devuelve una URL file:// compatible con los cargadores de imágenes."""
    return (IMAGENES_DIR / nombre_archivo).resolve().as_uri()


def imagen_establecimiento(nombre):
    """Devuelve la URL local del logo de un establecimiento, si existe."""
    nombre_archivo = IMAGENES_ESTABLECIMIENTOS.get(nombre)
    return _imagen_local(nombre_archivo) if nombre_archivo else ""


# Sustituye los placeholders del catálogo por los archivos entregados.
for _establecimiento, _productos in CATALOGO_PRODUCTOS.items():
    for _producto in _productos:
        nombre_archivo = IMAGENES_POR_ESTABLECIMIENTO.get(
            (_establecimiento, _producto["nombre"]),
            IMAGENES_LOCALES.get(_producto["nombre"]),
        )
        if nombre_archivo:
            _producto["imagen"] = _imagen_local(nombre_archivo)


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
