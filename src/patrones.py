"""
Patrones de texto (RegEx) y constantes usadas en la limpieza.

Cada patrón se define UNA sola vez acá. Si se ajusta un criterio,
se modifica en este archivo y se documenta el cambio.
"""

import numpy as np

PATRONES = {
    # Propiedades nuevas / en desarrollo (fuera del alcance: stock usado)
    "nuevo_fuerte": r"\bpozo\b|a estrenar|estrenar|en construcci[oó]n|en contruccion|pre[\s-]?venta",
    "nuevo_titulo": r"a estrenar|\bpozo\b|en construcci[oó]n|en contruccion|pre[\s-]?venta|emprend|desarrollo",

    # Publicaciones de alquiler cargadas como venta
    "alquiler_descripcion": r"departamento.{0,40}en alquiler|se alquila",
    "venta_titulo": r"venta|vende",

    # PH cargados como departamento
    "ph_titulo": r"\bPH\b",
    "ph_fuerte": (
        r"\bventa\s+(?:de\s+)?ph\b|"
        r"\bph\s+(?:de\s+)?\d|\bph\s+\d|"
        r"\btipo\s+ph\b|"
        r"\bdepto\.?\s*(?:tipo\s+)?ph\b|"
        r"\bdepartamento\s*(?:-|/)?\s*ph\b"
    ),

    # Expensas
    "sin_expensas": r"sin expensas|no paga expensas|no abona expensas",

    # Estado de la propiedad (señal imperfecta construida desde el texto)
    "necesita_obra_fuerte": r"a refaccionar|para refaccionar|a reciclar|para reciclar",
    "reciclada": r"reciclad[oa]|refaccionad[oa]",
    "buen_estado": r"excelente estado|muy buen estado|buen estado",
    "necesita_obra_debil": (
        r"para actualizar|a actualizar|a modernizar|para modernizar|"
        r"requiere refacci[oó]n|requiere refacciones|"
        r"necesita refacci[oó]n|necesita refacciones|"
        r"para reformar|a reformar|para remodelar|requiere actualizaci[oó]n|"
        r"potencial (?:de|para) (?:refacci[oó]n|renovaci[oó]n|modernizaci[oó]n|reciclar|refaccionar|modernizar)"
    ),
    "reciclada_debil": r"completamente remodelad[oa]|completamente hecho a nuevo|hech[oa] a nuevo completa",

    # Cochera (incluye plurales: "2 cocheras")
    "cochera": r"\b(?:cocheras?|garages?|garajes?|espacio guarda ?coches?)\b",
    "cochera_no_incluida": (
        r"cochera[s]?\s+no\s+incluida[s]?|"
        r"cochera[s]?\s+opcional(?:es)?|"
        r"posibilidad\s+de\s+(?:comprar|adquirir|alquilar)\s+(?:una\s+)?cochera|"
        r"cochera[s]?\s*\(opci[oó]n\s+de\s+alquiler\)"
    ),
}


def clasificar_estado(texto):
    """
    Estado_Propiedad a partir de título + descripción.

    Orden de prioridad (el primero que aplica gana):
      1. Necesita_obra (señal fuerte)
      2. Reciclada_refaccionada
      3. Buen_estado
      4. Necesita_obra (señal débil)
      5. Reciclada_refaccionada (señal débil)
      6. Sin_clasificar
    """
    def contiene(clave):
        return texto.str.contains(PATRONES[clave], case=False, na=False, regex=True)

    condiciones = [
        contiene("necesita_obra_fuerte"),
        contiene("reciclada"),
        contiene("buen_estado"),
        contiene("necesita_obra_debil"),
        contiene("reciclada_debil"),
    ]
    valores = [
        "Necesita_obra", "Reciclada_refaccionada", "Buen_estado",
        "Necesita_obra", "Reciclada_refaccionada",
    ]
    return np.select(condiciones, valores, default="Sin_clasificar")


# Negación: si alguna de estas palabras aparece en las 3 palabras previas
# a un match, el match no cuenta ("no requiere refacción", "sin reciclar").
# La ventana se corta en signos de puntuación: en "sin expensas, recientemente
# refaccionada" el "sin" no niega a "refaccionada".
NEGACION = r"\b(?:no|sin|ni|nunca|tampoco)\b(?:\s+[^\s,.;:!?]+){0,2}\s*$"


# Variables booleanas descriptivas extraídas del texto del aviso
# (se aplican sobre el texto normalizado: minúsculas y sin acentos)
TEXTO_BOOLEANAS = {
    "Luminoso": r"\b(?:luminos[oa]s?|muy luminos[oa]|excelente luminosidad|mucha luz|todo luz)\b",
    "Vista": (
        r"\b(?:vista abierta|vistas abiertas|vista panoramica|vistas panoramicas|"
        r"vista al rio|vista despejada|excelente vista)\b"
    ),
    "Silencioso": r"\b(?:silencios[oa]|muy tranquil[oa])\b",
    "Contrafrente": r"\bcontra ?frente\b",
    "Al_Frente": r"\b(?:al frente|a la calle)\b(?!\s+de[l ])",  # excluye "al frente del edificio"
    "Apto_Profesional": r"\bapto (?:profesional|prof\.?)\b",
    "Reciclado_Texto": (
        r"\b(?:reciclad[oa]s?|refaccionad[oa]s?|reciclado a nuevo|refaccionado a nuevo|"
        r"totalmente reciclad[oa]|totalmente refaccionad[oa])\b"
    ),
    "A_Refaccionar": (
        r"\b(?:a refaccionar|para refaccionar|a reciclar|para reciclar|"
        r"necesita refaccion|requiere refaccion|necesita reciclaje|requiere reciclaje)\b"
    ),
}

# Variables booleanas que se interpretan con control de negación
BOOLEANAS_CON_NEGACION = ["Luminoso", "Silencioso", "Reciclado_Texto", "A_Refaccionar"]


# Amenities: se combinan la lista estructurada de la fuente (columna Amenities)
# y las menciones en el texto. Clave = nombre de la variable.
AMENITIES = {
    "Pileta": {"lista": ["Pileta", "Pileta Climatizada", "Pileta Cubierta"],
               "texto": r"\b(?:pileta|piscina|swimming pool)\b"},
    "SUM": {"lista": ["Salón de usos múltiples - SUM"],
            "texto": r"\b(?:sum|salon de usos multiples|salon usos multiples)\b"},
    "Parrilla": {"lista": ["Parrilla"], "texto": r"\bparrillas?\b"},
    "Gimnasio": {"lista": ["Gimnasio"], "texto": r"\b(?:gimnasio|gym)\b"},
    "Laundry": {"lista": ["Laundry"], "texto": r"\b(?:laundry|lavanderia)\b"},
    "Seguridad": {"lista": ["Seguridad"],
                  "texto": r"\b(?:seguridad|vigilancia) (?:las )?24 ?(?:hs|horas)\b"},
    "Solarium": {"lista": ["Solarium"], "texto": r"\bsolarium\b"},
    "Balcon": {"lista": ["Balcón"], "texto": r"\bbalcon(?:es)?\b"},
    "Terraza": {"lista": ["Terraza"], "texto": r"\bterrazas?\b"},
    "Patio": {"lista": ["Patio"], "texto": r"\bpatios?\b"},
    "Ascensor": {"lista": ["Ascensor"], "texto": r"\bascensor(?:es)?\b"},
    "Baulera": {"lista": ["Baulera"], "texto": r"\bbauleras?\b"},
}


# Reciclado integral vs. parcial (para Estado_Propiedad y el PER)
RECICLADO_INTEGRAL = (
    r"\b(?:departamento|depto|dpto|unidad|propiedad|inmueble|piso|semipiso)\b.{0,50}"
    r"\b(?:totalmente|completamente|integralmente|todo)?\s*(?:reciclad[oa]|refaccionad[oa]|renovad[oa])\b"
    r"|\b(?:totalmente|completamente|integralmente|todo)\s+(?:reciclad[oa]|refaccionad[oa]|renovad[oa])\b"
    r"|\b(?:reciclado integral|refaccion integral|renovacion integral|renovad[oa] integralmente|hech[oa] a nuevo)\b"
)
RECICLADO_PARCIAL = (
    r"\b(?:cocinas?|banos?|toilettes?)\b.{0,30}\b(?:reciclad[oa]s?|refaccionad[oa]s?|renovad[oa]s?)\b"
    r"|\b(?:reciclad[oa]s?|refaccionad[oa]s?|renovad[oa]s?)\b.{0,30}\b(?:cocinas?|banos?|toilettes?)\b"
)


# Amenities: nombre de columna binaria -> valor(es) en la lista de RE/MAX
AMENITIES_BINARIAS = {
    "Tiene_Balcon": ["Balcón"],
    "Tiene_Ascensor": ["Ascensor"],
    "Tiene_Terraza": ["Terraza"],
    "Tiene_Parrilla": ["Parrilla"],
    "Tiene_SUM": ["Salón de usos múltiples - SUM"],
    "Tiene_Seguridad": ["Seguridad"],
    "Tiene_Aire_Acondicionado": ["Aire Acondicionado"],
    "Tiene_Baulera": ["Baulera"],
    "Tiene_Patio": ["Patio"],
    "Tiene_Laundry": ["Laundry"],
    "Tiene_Gimnasio": ["Gimnasio"],
    "Tiene_Solarium": ["Solarium"],
    "Tiene_Pileta": ["Pileta", "Pileta Climatizada", "Pileta Cubierta"],
}

# Rango aproximado de coordenadas de CABA (control grueso;
# la asignación fina de barrio se hace con el polígono oficial)
BBOX_CABA = {"lat": (-34.75, -34.50), "lon": (-58.55, -58.30)}
