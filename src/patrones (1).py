"""
Patrones de texto (RegEx) y constantes usadas en la limpieza.
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

    # Cochera
    "cochera": r"\bcochera\b|\bgarage\b|\bgaraje\b",
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
