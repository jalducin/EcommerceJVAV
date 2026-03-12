"""
Script de seed: inserta 20 productos de ejemplo en la base de datos.
Uso: poetry run python seed_products.py
"""

import asyncio

from backend.database import AsyncSessionLocal
from backend.models.product import Product

PRODUCTS = [
    {
        "name": "Casco de Acero Inoxidable Pro",
        "description": "Casco de seguridad fabricado en acero inoxidable 304. Resistente a impactos y corrosión. Certificado EN 397.",
        "price": 299.99,
        "stock": 15,
        "category": "Protección",
        "images": ["https://placehold.co/600x400/1A1A2E/D4AF37?text=Casco+Pro"],
    },
    {
        "name": "Guantes de Cuero Industrial",
        "description": "Guantes de cuero genuino reforzado con forro de kevlar. Protección mecánica nivel 4.",
        "price": 89.99,
        "stock": 42,
        "category": "Protección",
        "images": ["https://placehold.co/600x400/1A1A2E/C0C0C0?text=Guantes"],
    },
    {
        "name": "Herramienta Multifunción Titanio",
        "description": "18 funciones en una sola herramienta de titanio grado aeronáutico. Incluye funda de cuero.",
        "price": 159.99,
        "stock": 28,
        "category": "Herramientas",
        "images": ["https://placehold.co/600x400/1A1A2E/B87333?text=Multifunci%C3%B3n"],
    },
    {
        "name": "Set Llaves Allen Cromo-Vanadio",
        "description": "Set completo de 15 llaves Allen en acero cromo-vanadio. Acabado cromado anti-oxidación.",
        "price": 49.99,
        "stock": 65,
        "category": "Herramientas",
        "images": ["https://placehold.co/600x400/1A1A2E/D4AF37?text=Llaves+Allen"],
    },
    {
        "name": "Cadena de Acero Templado 10mm",
        "description": "Cadena de seguridad en acero templado de 10mm. Resistencia a tracción: 3500 kg. Longitud: 2 metros.",
        "price": 74.99,
        "stock": 33,
        "category": "Seguridad",
        "images": ["https://placehold.co/600x400/1A1A2E/C0C0C0?text=Cadena"],
    },
    {
        "name": "Cuchillo de Caza Acero Damasco",
        "description": "Hoja en acero damasco 256 capas, mango en madera de nogal con virolas de cobre. Incluye vaina de cuero.",
        "price": 349.99,
        "stock": 8,
        "category": "Cuchillería",
        "images": ["https://placehold.co/600x400/1A1A2E/B87333?text=Cuchillo"],
    },
    {
        "name": "Brújula Náutica de Latón",
        "description": "Brújula náutica vintage en latón macizo. Precisión ±0.5°. Incluye estuche de madera.",
        "price": 129.99,
        "stock": 20,
        "category": "Navegación",
        "images": ["https://placehold.co/600x400/1A1A2E/D4AF37?text=Br%C3%BAjula"],
    },
    {
        "name": "Linterna Táctica LED 1000 Lúmenes",
        "description": "Linterna táctica en aluminio aeronáutico. 1000 lúmenes, 5 modos de iluminación. Resistente al agua IP68.",
        "price": 69.99,
        "stock": 50,
        "category": "Iluminación",
        "images": ["https://placehold.co/600x400/1A1A2E/C0C0C0?text=Linterna"],
    },
    {
        "name": "Reloj Cronógrafo Acero 316L",
        "description": "Cronógrafo mecánico en acero quirúrgico 316L. Resistente al agua 200m. Cristal de zafiro.",
        "price": 899.99,
        "stock": 5,
        "category": "Accesorios",
        "images": ["https://placehold.co/600x400/1A1A2E/D4AF37?text=Reloj"],
    },
    {
        "name": "Correa de Nylon Táctico 40mm",
        "description": "Correa táctica de nylon balístico con hebilla de acero inoxidable. Compatible con relojes 40-42mm.",
        "price": 34.99,
        "stock": 80,
        "category": "Accesorios",
        "images": ["https://placehold.co/600x400/1A1A2E/C0C0C0?text=Correa"],
    },
    {
        "name": "Cinta Métrica Inoxidable 10m",
        "description": "Cinta métrica en acero inoxidable con funda de goma anti-golpe. Precisión clase II.",
        "price": 29.99,
        "stock": 45,
        "category": "Herramientas",
        "images": ["https://placehold.co/600x400/1A1A2E/B87333?text=Cinta+M%C3%A9trica"],
    },
    {
        "name": "Mazo de Cobre 1kg",
        "description": "Mazo de cobre puro 1 kg. Ideal para ajustes sin marcar superficies metálicas delicadas.",
        "price": 79.99,
        "stock": 18,
        "category": "Herramientas",
        "images": ["https://placehold.co/600x400/1A1A2E/B87333?text=Mazo"],
    },
    {
        "name": "Candado de Alta Seguridad Acero",
        "description": "Candado de disco en acero endurecido. Certificado grado 5. Resistente al corte con cizalla.",
        "price": 59.99,
        "stock": 30,
        "category": "Seguridad",
        "images": ["https://placehold.co/600x400/1A1A2E/C0C0C0?text=Candado"],
    },
    {
        "name": "Caja Fuerte Acero 3mm",
        "description": "Caja fuerte de pared en acero laminado 3mm. Cerradura electrónica con código y llave. 20 litros.",
        "price": 249.99,
        "stock": 12,
        "category": "Seguridad",
        "images": ["https://placehold.co/600x400/1A1A2E/D4AF37?text=Caja+Fuerte"],
    },
    {
        "name": "Carabiner HMS Aluminio 7075",
        "description": "Mosquetón HMS en aluminio 7075 T6. Resistencia a carga: 23 kN. Certificado EN 12275.",
        "price": 19.99,
        "stock": 120,
        "category": "Escalada",
        "images": ["https://placehold.co/600x400/1A1A2E/C0C0C0?text=Mosquet%C3%B3n"],
    },
    {
        "name": "Piolet de Alpinismo Titanio",
        "description": "Piolet técnico con cabeza en titanio y mango de fibra de carbono. Peso: 310g. Certificado UIAA.",
        "price": 189.99,
        "stock": 7,
        "category": "Escalada",
        "images": ["https://placehold.co/600x400/1A1A2E/D4AF37?text=Piolet"],
    },
    {
        "name": "Pelacables Ergonómico Pro",
        "description": "Pelacables automático con mandíbulas de acero inoxidable. Mangas de 0.5-6mm². Mango bimaterial.",
        "price": 44.99,
        "stock": 55,
        "category": "Herramientas",
        "images": ["https://placehold.co/600x400/1A1A2E/B87333?text=Pelacables"],
    },
    {
        "name": "Nivel Láser Autonivelante",
        "description": "Nivel láser de línea cruzada autonivelante. Alcance 30m, precisión ±0.3mm/m. Incluye trípode.",
        "price": 139.99,
        "stock": 22,
        "category": "Herramientas",
        "images": ["https://placehold.co/600x400/1A1A2E/C0C0C0?text=Nivel+L%C3%A1ser"],
    },
    {
        "name": "Esposas de Acero Profesionales",
        "description": "Esposas de seguridad en acero niquelado. Doble cierre de seguridad. Incluye 2 llaves.",
        "price": 39.99,
        "stock": 0,
        "category": "Seguridad",
        "images": ["https://placehold.co/600x400/1A1A2E/D4AF37?text=Esposas"],
    },
    {
        "name": "Kit Supervivencia Ultra Premium",
        "description": "Kit completo de 32 piezas en caja de aluminio: navaja, linterna, silbato, encendedor, brújula, botiquín y más.",
        "price": 199.99,
        "stock": 10,
        "category": "Supervivencia",
        "images": ["https://placehold.co/600x400/1A1A2E/D4AF37?text=Kit+Supervivencia"],
    },
]


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        for data in PRODUCTS:
            product = Product(**data)
            db.add(product)
        await db.commit()
    print(f"✅ {len(PRODUCTS)} productos creados correctamente")


if __name__ == "__main__":
    asyncio.run(seed())
