"""
Extractores de prueba para fuentes alternativas evaluadas y descartadas.

Antes de elegir RE/MAX como fuente principal se probaron otros portales (ver el
anexo de notebooks/01_extraccion_remax.ipynb). Este módulo conserva el código de
esas pruebas como evidencia; no forma parte del flujo del proyecto.

- Cabaprop: consulta la API del sitio barrio por barrio. Se descartó por su bajo
  volumen (2.591 avisos). Función principal: cabaprop_run_scraper().
- Zonaprop: recorre el listado paginado con requests y BeautifulSoup. Desde Google
  Colab el sitio respondió con un bloqueo (HTTP 403). Función principal:
  zonaprop_run_scraper(paginas_por_corrida=...).
"""

import json
import logging
import os
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup


# ======================================================================
# CABAPROP
# ======================================================================


cabaprop_logger = logging.getLogger(__name__)

CABAPROP_API_URL = "https://cabaprop.com.ar/api/v1/properties/find-properties"

CABAPROP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Referer": "https://cabaprop.com.ar/propiedades/comprar-casa-departamento-ph",
    "Origin": "https://cabaprop.com.ar",
}

CABAPROP_LIMIT = 12  # confirmado: el que usa el sitio real
CABAPROP_SLEEP_TIME = 0.5

# Lista completa de barrios de CABA según el sitio (endpoint
# /api/v1/utils/barrios-flat) — recorremos uno por uno para que cada
# consulta quede muy por debajo del límite de profundidad de
# paginación que corta la búsqueda general de CABA entera (~2000).
CABAPROP_BARRIOS = {
    1: "Abasto", 2: "Agronomía", 3: "Almagro", 4: "Almagro Norte", 5: "Almagro Sur",
    6: "Balvanera", 7: "Balvanera Congreso", 8: "Balvanera Once", 9: "Barracas",
    10: "Barrio Norte", 11: "Barrio Norte La Isla", 12: "Barrio Norte Parque Las Heras",
    13: "Barrio Norte Recoleta", 14: "Belgrano", 15: "Belgrano Barrancas", 16: "Belgrano C",
    17: "Belgrano La Imprenta", 18: "Belgrano R", 19: "Boedo", 20: "Caballito",
    21: "Caballito Barrio Inglés", 22: "Caballito Cid Campeador", 23: "Caballito Norte",
    24: "Caballito Parque Rivadavia", 25: "Caballito Primera Junta", 26: "Caballito Sur",
    27: "Chacarita", 28: "Coghlan", 29: "Colegiales", 30: "Constitución", 31: "Flores",
    32: "Flores Norte", 33: "Flores Sur", 34: "Floresta", 35: "Floresta Norte",
    36: "Floresta Sur", 37: "La Boca", 38: "La Paternal", 39: "Liniers", 40: "Mataderos",
    41: "Microcentro / Centro", 42: "Monserrat", 43: "Monte Castro", 44: "Nuñez",
    45: "Nuñez Lomas", 46: "Nuñez River", 47: "Palermo", 48: "Palermo Botánico",
    49: "Palermo Boulevard", 50: "Palermo Chico", 51: "Palermo Hollywood",
    52: "Palermo Las Cañitas", 53: "Palermo Pacífico", 54: "Palermo Plaza Italia",
    55: "Palermo Soho", 56: "Palermo Viejo", 57: "Parque Avellaneda",
    58: "Parque Centenario", 59: "Parque Chacabuco", 60: "Parque Chas",
    61: "Parque Patricios", 62: "Pompeya", 63: "Primera Junta", 64: "Puerto Madero",
    65: "Retiro", 66: "Retiro Catalinas", 67: "Retiro Plaza San Martín", 68: "Saavedra",
    69: "San Cristóbal", 70: "San Nicolás", 71: "San Nicolás Tribunales", 72: "San Telmo",
    73: "Vélez Sarsfield", 74: "Versalles", 75: "Villa Crespo", 76: "Villa del Parque",
    77: "Villa Devoto", 78: "Villa General Mitre", 79: "Villa Lugano", 80: "Villa Luro",
    81: "Villa Ortúzar", 82: "Villa Pueyrredón", 83: "Villa Real", 84: "Villa Riachuelo",
    85: "Villa Santa Rita", 86: "Villa Soldati", 87: "Villa Urquiza", 88: "Recoleta",
}

CABAPROP_OUTPUT_DIR = "output"

CABAPROP_SESSION = requests.Session()
CABAPROP_SESSION.headers.update(CABAPROP_HEADERS)


def cabaprop_get_page(offset, barrio_id):

    params = {
        "offset": offset,
        "limit": CABAPROP_LIMIT,
        "orderBy": "created_at",
        "sort": "desc",
    }

    body = {
        "operationType": 1,
        "propertyTypes": [2, 1, 3],
        "barrios": [barrio_id],
        "ambiences": [],
        "antiquity": "",
        "bathrooms": 0,
        "bedrooms": [],
        "characteristics": [],
        "extras": [],
        "garages": 0,
        "price": {"currency": "ARS", "min": 0, "max": 0, "tag": "pesos"},
        "surface": {"tag": "superficieTotal", "type": "totalSurface", "min": "", "max": ""},
    }

    try:
        r = CABAPROP_SESSION.post(CABAPROP_API_URL, params=params, json=body, timeout=20)

        if r.status_code == 500:
            # Puede seguir siendo el límite de profundidad, incluso
            # acotado por barrio, en barrios muy grandes
            return None

        r.raise_for_status()
        return r.json()

    except requests.exceptions.RequestException as e:
        cabaprop_logger.error(f"Error en barrio {barrio_id}, offset {offset}: {e}")

    return None


def cabaprop_parse_property(item, barrio_nombre_filtro):

    try:
        location = item.get("location") or {}
        surface = item.get("surface") or {}
        antiquity = item.get("antiquity") or {}
        price = item.get("price") or {}
        characteristics = item.get("characteristics") or {}
        garages = characteristics.get("garages") or {}
        publication = item.get("publication") or {}
        seller_address = publication.get("seller_address") or {}
        search_location = seller_address.get("search_location") or {}
        neighborhood = search_location.get("neighborhood") or {}
        extras = item.get("extras") or {}
        adicionales = extras.get("adicionales") or {}

        amenities_activos = [k for k, v in adicionales.items() if v is True] if adicionales else []

        return {
            "Fuente": "CABAPROP",
            "ID": item.get("_id"),
            "ML_ID": item.get("ml_id"),
            "Titulo": item.get("title"),
            "Descripcion": item.get("description"),
            "Estado_Publicacion": item.get("status"),
            "Operacion_Tipo": item.get("operation_type"),
            "Propiedad_Tipo": item.get("property_type"),
            "Direccion": location.get("street"),
            "Altura": location.get("number"),
            "Barrio": neighborhood.get("name") or barrio_nombre_filtro,
            "Localidad": location.get("area_level_2"),
            "Latitud": location.get("lat"),
            "Longitud": location.get("lng"),
            "Superficie_Total_m2": surface.get("totalSurface"),
            "Superficie_Cubierta_m2": surface.get("coveredSurface"),
            "Antiguedad": antiquity.get("years"),
            "Moneda": publication.get("currency_id"),
            "Precio_Valor": price.get("total"),
            "Expensas": price.get("expenses"),
            "Ambientes": characteristics.get("ambience"),
            "Dormitorios": characteristics.get("bedrooms"),
            "Baños": characteristics.get("bathrooms"),
            "Cocheras": garages.get("quantity"),
            "Apto_Credito": characteristics.get("aptCredito"),
            "Apto_Profesional": characteristics.get("aptProfesional"),
            "Apto_Mascota": characteristics.get("aptMascota"),
            "Amenities": " | ".join(amenities_activos) if amenities_activos else None,
            "Fecha_Publicacion": publication.get("start_time"),
            "Fecha_Vencimiento": publication.get("expiration_time"),
            "Link": publication.get("permalink"),
        }

    except Exception as e:
        cabaprop_logger.error(f"Error procesando propiedad {item.get('_id')}: {e}")
        return None


def cabaprop_recorrer_barrio(barrio_id, barrio_nombre, all_data, seen_ids):

    nuevas_barrio = 0
    offset = 0

    while True:

        data = cabaprop_get_page(offset, barrio_id)

        if data is None:
            cabaprop_logger.warning(f"  {barrio_nombre}: se cortó en offset {offset} (límite del backend)")
            break

        results = data.get("result", [])

        if not results:
            break

        for item in results:
            parsed = cabaprop_parse_property(item, barrio_nombre)
            if parsed and parsed["ID"] and parsed["ID"] not in seen_ids:
                seen_ids.add(parsed["ID"])
                all_data.append(parsed)
                nuevas_barrio += 1

        offset += CABAPROP_LIMIT
        time.sleep(CABAPROP_SLEEP_TIME)

    return nuevas_barrio


def cabaprop_run_scraper():
    os.makedirs(CABAPROP_OUTPUT_DIR, exist_ok=True)

    all_data = []
    seen_ids = set()

    print("\n" + "=" * 60)
    print(f"INICIANDO SCRAPER CABAPROP — CABA, por barrio ({len(CABAPROP_BARRIOS)} barrios)")
    print("=" * 60)

    for i, (barrio_id, barrio_nombre) in enumerate(CABAPROP_BARRIOS.items(), start=1):

        print(f"\n[{i}/{len(CABAPROP_BARRIOS)}] {barrio_nombre} (id={barrio_id})")

        nuevas = cabaprop_recorrer_barrio(barrio_id, barrio_nombre, all_data, seen_ids)

        print(f"   Propiedades nuevas: {nuevas} | Total acumulado: {len(all_data)}")

        # Guardado incremental — si algo corta a mitad de camino, no se pierde nada
        pd.DataFrame(all_data).to_csv(
            os.path.join(CABAPROP_OUTPUT_DIR, "cabaprop_caba_venta.csv"),
            index=False, encoding="utf-8-sig"
        )

    if not all_data:
        print("\n No se obtuvieron datos.")
        return None

    df = pd.DataFrame(all_data)

    csv_path = os.path.join(CABAPROP_OUTPUT_DIR, "cabaprop_caba_venta.csv")
    xlsx_path = os.path.join(CABAPROP_OUTPUT_DIR, "cabaprop_caba_venta.xlsx")

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_excel(xlsx_path, index=False)

    print("\n" + "=" * 60)
    print("SCRAPING FINALIZADO")
    print("=" * 60)
    print(f"Total de avisos: {len(df)}")
    print(f"\nCSV: {csv_path}")
    print(f"Excel: {xlsx_path}")

    print("\nCOBERTURA DE CAMPOS CLAVE (no nulos / total):")
    for columna in ["Descripcion", "Antiguedad", "Fecha_Publicacion", "Apto_Credito", "Amenities", "Barrio"]:
        if columna in df.columns:
            no_nulos = df[columna].notna().sum()
            print(f"  {columna}: {no_nulos}/{len(df)}")

    return df


# ======================================================================
# ZONAPROP
# ======================================================================


zonaprop_logger = logging.getLogger(__name__)

ZONAPROP_BASE_URL = "https://www.zonaprop.com.ar/casas-departamentos-ph-edificios-venta-capital-federal.html"

ZONAPROP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9",
}

ZONAPROP_MAX_PAGES_POR_CORRIDA = 8  # límite prudente por sesión, por debajo del punto donde aparece el bloqueo
ZONAPROP_SLEEP_TIME = 2.0  # más pausado, para parecer menos "bot"

ZONAPROP_OUTPUT_DIR = "output"

ZONAPROP_CSV_PATH = os.path.join(ZONAPROP_OUTPUT_DIR, "zonaprop_caba_venta.csv")
ZONAPROP_PROGRESS_PATH = os.path.join(ZONAPROP_OUTPUT_DIR, "zonaprop_progress.txt")

# Tipos de propiedad válidos conocidos — cualquier otra cosa que salga
# del parseo del alt de la imagen (códigos internos, nombres de foto
# sueltos, etc.) se descarta en vez de dejarla "sucia" en el dataset.
ZONAPROP_TIPOS_VALIDOS = {
    "departamento", "casa", "ph", "edificio", "oficina", "local",
    "terreno", "lote", "cochera", "galpón", "galpon", "depósito",
    "deposito", "quinta", "campo", "hotel", "fondo de comercio"
}

ZONAPROP_SESSION = requests.Session()
ZONAPROP_SESSION.headers.update(ZONAPROP_HEADERS)


def zonaprop_leer_ultima_pagina():
    """Lee hasta qué página se llegó en la corrida anterior (0 si es la primera vez)."""
    if os.path.exists(ZONAPROP_PROGRESS_PATH):
        with open(ZONAPROP_PROGRESS_PATH, "r") as f:
            contenido = f.read().strip()
            if contenido.isdigit():
                return int(contenido)
    return 0


def zonaprop_guardar_ultima_pagina(pagina):
    with open(ZONAPROP_PROGRESS_PATH, "w") as f:
        f.write(str(pagina))


def zonaprop_get_page_url(page):
    if page == 1:
        return ZONAPROP_BASE_URL
    return ZONAPROP_BASE_URL.replace(".html", f"-pagina-{page}.html")


def zonaprop_extraer_id_de_url(url):
    """Saca el ID numérico del final de una URL de Zonaprop (ej: ...-56135149.html -> 56135149)."""
    if not url:
        return None
    m = re.search(r'-(\d+)\.html', url)
    return m.group(1) if m else None


def zonaprop_parsear_jsonld_listado(html_text):
    """
    El listado trae, entre sus varios bloques <script type="application/ld+json">,
    uno con mainEntity que contiene la DESCRIPCIÓN COMPLETA y la fecha real
    de publicación (datePosted) de cada propiedad de la página — gratis,
    sin pedir la ficha individual. Devuelve un dict {id: {...}}.
    """

    resultado = {}

    bloques = re.findall(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        html_text, re.DOTALL
    )

    for bloque in bloques:
        try:
            data = json.loads(bloque)
        except json.JSONDecodeError:
            continue

        if not isinstance(data, dict) or "mainEntity" not in data:
            continue

        for entrada in data["mainEntity"]:
            prop_id = zonaprop_extraer_id_de_url(entrada.get("url"))
            if prop_id:
                resultado[prop_id] = {
                    "Descripcion_Completa": entrada.get("description"),
                    "Fecha_Publicacion": entrada.get("datePosted"),
                }

        break  # ya encontramos el bloque bueno, no hace falta seguir

    return resultado


def zonaprop_parse_card(card):

    try:
        property_id = card.get("data-id")

        to_posting = card.get("data-to-posting") or ""
        to_posting_limpio = to_posting.split("?")[0]
        link = f"https://www.zonaprop.com.ar{to_posting_limpio}" if to_posting_limpio else None

        precio_tag = card.find(attrs={"data-qa": "POSTING_CARD_PRICE"})
        precio_texto = precio_tag.get_text(strip=True) if precio_tag else None

        moneda = None
        precio = None
        if precio_texto:
            m = re.match(r"([A-Za-z$]+)\s*([\d.,]+)", precio_texto)
            if m:
                moneda = m.group(1)
                precio = float(m.group(2).replace(".", "").replace(",", "."))

        expensas_tag = card.find(attrs={"data-qa": "expensas"})
        expensas_texto = expensas_tag.get_text(strip=True) if expensas_tag else None
        expensas = None
        if expensas_texto:
            m = re.search(r"([\d.,]+)", expensas_texto)
            if m:
                expensas = float(m.group(1).replace(".", "").replace(",", "."))

        features_tag = card.find(attrs={"data-qa": "POSTING_CARD_FEATURES"})
        superficie_total = ambientes = dormitorios = banos = None

        if features_tag:
            for span in features_tag.find_all("span"):
                texto = span.get_text(strip=True)
                if "m²" in texto:
                    m = re.search(r"([\d.,]+)\s*m²", texto)
                    if m:
                        superficie_total = float(m.group(1).replace(".", "").replace(",", "."))
                elif "amb" in texto:
                    m = re.search(r"(\d+)", texto)
                    if m:
                        ambientes = int(m.group(1))
                elif "dorm" in texto:
                    m = re.search(r"(\d+)", texto)
                    if m:
                        dormitorios = int(m.group(1))
                elif "baño" in texto:
                    m = re.search(r"(\d+)", texto)
                    if m:
                        banos = int(m.group(1))

        location_block = card.find("div", class_=lambda c: c and "location-block" in c)
        direccion = None
        if location_block:
            h4s = location_block.find_all("h4")
            if h4s:
                direccion = h4s[0].get_text(strip=True)

        ubicacion_tag = card.find(attrs={"data-qa": "POSTING_CARD_LOCATION"})
        ubicacion_texto = ubicacion_tag.get_text(strip=True) if ubicacion_tag else None
        barrio = ubicacion_texto.split(",")[0].strip() if ubicacion_texto else None

        descripcion_tag = card.find(attrs={"data-qa": "POSTING_CARD_DESCRIPTION"})
        descripcion_resumida = descripcion_tag.get_text(strip=True) if descripcion_tag else None

        tipo_propiedad = titulo = None
        gallery = card.find("div", class_=lambda c: c and "gallery-container" in c)
        img_tag = gallery.find("img") if gallery else None

        if img_tag and img_tag.get("alt") and "·" in img_tag["alt"]:
            partes = [p.strip() for p in img_tag["alt"].split("·")]
            if partes and partes[0].lower() in ZONAPROP_TIPOS_VALIDOS:
                tipo_propiedad = partes[0]
            if len(partes) >= 4:
                titulo = partes[-1]

        precio_m2 = round(precio / superficie_total, 2) if (precio and superficie_total and superficie_total > 0) else None

        return {
            "Fuente": "Zonaprop",
            "ID": property_id,
            "Titulo": titulo,
            "Tipo_Propiedad": tipo_propiedad,

            "Moneda": moneda,
            "Precio_Valor": precio,
            "Expensas": expensas,

            "Superficie_Total_m2": superficie_total,
            "Precio_m2_Total": precio_m2,

            "Ambientes": ambientes,
            "Dormitorios": dormitorios,
            "Baños": banos,

            "Direccion": direccion,
            "Barrio": barrio,
            "Ubicacion": ubicacion_texto,

            "Descripcion_Resumida": descripcion_resumida,

            "Link": link,
        }

    except Exception as e:
        zonaprop_logger.error(f"Error procesando una tarjeta: {e}")
        return None


def zonaprop_run_scraper(paginas_por_corrida=ZONAPROP_MAX_PAGES_POR_CORRIDA):
    os.makedirs(ZONAPROP_OUTPUT_DIR, exist_ok=True)


    # CARGAR LO YA CONSEGUIDO EN CORRIDAS ANTERIORES (si existe)


    all_data = []
    seen_ids = set()

    if os.path.exists(ZONAPROP_CSV_PATH):
        df_previo = pd.read_csv(ZONAPROP_CSV_PATH, dtype={"ID": str})
        all_data = df_previo.to_dict("records")
        seen_ids = set(df_previo["ID"].dropna().astype(str))
        print(f" Cargados {len(all_data)} avisos de corridas anteriores.")

    pagina_inicial = zonaprop_leer_ultima_pagina() + 1
    pagina_final = pagina_inicial + paginas_por_corrida - 1

    print(f"[DEBUG] paginas_por_corrida recibido: {paginas_por_corrida}")
    print(f"[DEBUG] pagina_inicial: {pagina_inicial} | pagina_final: {pagina_final}")

    print("\n" + "=" * 60)
    print("INICIANDO SCRAPER ZONAPROP — CABA")
    print(f"Retomando desde la página {pagina_inicial} hasta la {pagina_final}")
    print("=" * 60)

    for page in range(pagina_inicial, pagina_final + 1):

        url = zonaprop_get_page_url(page)

        print(f"\n--- PÁGINA {page} ---")
        print(f"URL: {url}")

        try:
            r = ZONAPROP_SESSION.get(url, timeout=20)
        except requests.exceptions.RequestException as e:
            zonaprop_logger.error(f"Error en página {page}: {e}")
            time.sleep(3)
            continue

        print(f"Status: {r.status_code} | Largo del HTML: {len(r.text)}")

        if r.status_code != 200:
            print(" Status distinto de 200 — probablemente bloqueado. Cortando esta corrida.")
            print("   (la próxima vez que corras el script, retoma desde esta misma página)")
            print(r.text[:500])
            break

        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.find_all("div", attrs={"data-posting-type": "PROPERTY"})

        if not cards:
            print("\n 0 tarjetas encontradas — fin real del listado.")
            zonaprop_guardar_ultima_pagina(page)  # no volver a intentar esta página
            break

        print(f"Tarjetas encontradas: {len(cards)}")

        jsonld_por_id = zonaprop_parsear_jsonld_listado(r.text)
        print(f"Propiedades con descripción completa (JSON-LD): {len(jsonld_por_id)}")

        filas_pagina = []

        for card in cards:

            parsed = zonaprop_parse_card(card)

            if not parsed or not parsed["ID"] or parsed["ID"] in seen_ids:
                continue

            seen_ids.add(parsed["ID"])

            extra = jsonld_por_id.get(parsed["ID"], {})
            parsed["Descripcion_Completa"] = extra.get("Descripcion_Completa")
            parsed["Fecha_Publicacion"] = extra.get("Fecha_Publicacion")

            filas_pagina.append(parsed)

        all_data.extend(filas_pagina)

        print(f"Nuevas: {len(filas_pagina)} | Total acumulado: {len(all_data)}")

        # Guardamos el progreso YA, página por página — así si el
        # bloqueo aparece en la página siguiente, no se pierde nada
        # de lo ya conseguido en esta corrida.
        zonaprop_guardar_ultima_pagina(page)

        df_parcial = pd.DataFrame(all_data)
        df_parcial.to_csv(ZONAPROP_CSV_PATH, index=False, encoding="utf-8-sig")

        time.sleep(ZONAPROP_SLEEP_TIME)

    if not all_data:
        print("\n No se obtuvieron datos.")
        return None

    df = pd.DataFrame(all_data)

    csv_path = ZONAPROP_CSV_PATH
    xlsx_path = os.path.join(ZONAPROP_OUTPUT_DIR, "zonaprop_caba_venta.xlsx")

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_excel(xlsx_path, index=False)

    print("\n" + "=" * 60)
    print("SCRAPING FINALIZADO")
    print("=" * 60)
    print(f"Total de avisos: {len(df)}")
    print(f"\nCSV: {csv_path}")
    print(f"Excel: {xlsx_path}")

    print("\nTIPOS DE PROPIEDAD:")
    print(df["Tipo_Propiedad"].value_counts(dropna=False))

    print("\nCOBERTURA DE CAMPOS ENRIQUECIDOS:")
    for columna in ["Descripcion_Completa", "Fecha_Publicacion"]:
        if columna in df.columns:
            no_nulos = df[columna].notna().sum()
            print(f"  {columna}: {no_nulos}/{len(df)}")

    return df
