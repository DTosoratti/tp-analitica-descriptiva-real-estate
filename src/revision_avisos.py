"""
Revisión de la lista de visitas: señales de que un aviso no es comparable.

El benchmark compara precios de departamentos usados que se venden enteros, con
destino vivienda y bien ubicados en el mapa. Algunos avisos que aparecen muy
baratos no cumplen alguno de esos supuestos, y su "descuento" no es una
oportunidad sino una diferencia de producto. Este módulo los detecta de forma
automática; la notebook 09 lo complementa con la lectura manual de los primeros
puestos (`data/validation/revision_lista_visitas.csv`).

Dos niveles:

- **Excluir**: el precio publicado no es comparable con el de sus comparables
  (precio parcial o anticipo, derechos parciales como nuda propiedad, unidad
  escriturada con otro destino) o la ubicación es inconsistente, por lo que el
  benchmark se calculó contra el barrio equivocado.
- **Verificar**: hay una razón identificable para el descuento que conviene
  confirmar en la visita (uso no residencial, PH, inquilino, sucesión, posible
  duplicado).
"""

import unicodedata

import numpy as np
import pandas as pd

# --- Patrones de texto (sobre título + descripción en minúsculas) ---------------

PATRONES_EXCLUIR = {
    "Precio_Parcial": (
        r"precio publicado (?:es|corresponde) (?:del|al) anticipo"
        r"|precio publicado var[ií]a con la financiaci"
    ),
    "Derechos_Parciales": r"nuda propiedad|usufructo|derechos y acciones",
    "Escritura_Otro_Uso": (
        r"(?:escritura|reglamento).{0,80}(?:consta|figura|est[aá]) como (?:cochera|oficina|local|baulera)"
        r"|consta como (?:cochera|oficina|local)"
    ),
}

PATRONES_VERIFICAR = {
    "Uso_No_Residencial": r"\b(?:oficina|consultorio|local comercial)\b",  # solo en el título
    "Tipologia_PH": r"\bph\b",
    "Con_Inquilino": (
        r"alquilad[oa] hasta|contrato de alquiler vigente|se vende con (?:renta|contrato)"
        r"|con renta hasta|renta asegurada"
    ),
    "Sucesion": r"sucesi[oó]n|tracto abreviado",
}

# Nombres de barrio informales que usan los avisos → barrios oficiales posibles
BARRIOS_INFORMALES = {
    "ABASTO": ["BALVANERA", "ALMAGRO"],
    "BAJO BELGRANO": ["BELGRANO", "NUNEZ"],
    "BARRANCAS DE BELGRANO": ["BELGRANO"],
    "BARRIO CHINO": ["BELGRANO"],
    "BARRIO NORTE": ["RECOLETA", "BALVANERA", "RETIRO"],
    "BARRIO RIVER": ["BELGRANO", "NUNEZ"],
    "BARRIO SAMORE": ["VILLA LUGANO"],
    "BELGRANO C": ["BELGRANO"],
    "BELGRANO CHICO": ["BELGRANO"],
    "BELGRANO R": ["BELGRANO"],
    "BOTANICO": ["PALERMO"],
    "CABALLITO NORTE": ["CABALLITO"],
    "CABALLITO SUR": ["CABALLITO"],
    "CENTRO / MICROCENTRO": ["SAN NICOLAS", "MONSERRAT", "RETIRO"],
    "CID CAMPEADOR": ["CABALLITO", "VILLA CRESPO", "FLORES"],
    "CONGRESO": ["BALVANERA", "MONSERRAT", "SAN NICOLAS"],
    "LA PATERNAL": ["PATERNAL"],
    "LAS CANITAS": ["PALERMO"],
    "ONCE": ["BALVANERA"],
    "PALERMO CHICO": ["PALERMO"],
    "PALERMO HOLLYWOOD": ["PALERMO"],
    "PALERMO NUEVO": ["PALERMO"],
    "PALERMO SOHO": ["PALERMO"],
    "PALERMO VIEJO": ["PALERMO"],
    "PARQUE CENTENARIO": ["CABALLITO", "ALMAGRO", "VILLA CRESPO"],
    "PLAZA SAN MARTIN": ["RETIRO"],
    "VILLA GENERAL MITRE": ["VILLA GRAL. MITRE"],
}

# Distancia (km) entre el punto del aviso y el centro del barrio que declara el
# aviso a partir de la cual la diferencia no es un caso de límite entre barrios
# vecinos. Entre los 698 avisos cuyo barrio declarado difiere del oficial, la
# mediana es 1,2 km y el percentil 75, 1,5 km; solo 11 superan los 3 km.
DISTANCIA_UBICACION_KM = 3.0


def _norm(s):
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper().strip()


def _texto(df):
    return (df["Titulo"].fillna("") + " " + df["Descripcion"].fillna("")).str.lower()


def ubicacion_inconsistente(df, df_mercado=None, umbral_km=DISTANCIA_UBICACION_KM):
    """
    Marca los avisos cuyo barrio declarado (columna `Barrio` del aviso) no
    coincide con el barrio oficial asignado por coordenadas y cuyo punto está a
    más de `umbral_km` del centro (mediana de coordenadas) del barrio declarado.

    Devuelve (flag, distancia_km). `df_mercado` es la base con la que se calculan
    los centros de cada barrio (por defecto, `df`).
    """
    base = df if df_mercado is None else df_mercado
    centros = (base.assign(_of=base["Barrio_Oficial"].map(_norm))
               .groupby("_of")[["Latitud", "Longitud"]].median())
    declarado = df["Barrio"].map(_norm).map(lambda b: BARRIOS_INFORMALES.get(b, [b]))
    oficial = df["Barrio_Oficial"].map(_norm)
    km_lon = 111.32 * np.cos(np.radians(34.6))

    dist = []
    for lat, lon, decl in zip(df["Latitud"], df["Longitud"], declarado):
        ds = [np.hypot((lat - centros.at[b, "Latitud"]) * 110.57,
                       (lon - centros.at[b, "Longitud"]) * km_lon)
              for b in decl if b in centros.index]
        dist.append(min(ds) if ds else np.nan)
    dist = pd.Series(dist, index=df.index)
    distinto = pd.Series([o not in d for o, d in zip(oficial, declarado)], index=df.index)
    return distinto & dist.gt(umbral_km), dist.where(distinto)


def posibles_duplicados(df):
    """Avisos con la misma dirección, precio y ambientes que otro aviso de `df`."""
    clave = df["Direccion"].fillna("").str.lower().str.strip() + "|" + \
        df["Precio_Valor"].astype(str) + "|" + df["Ambientes"].astype(str)
    return clave.duplicated(keep=False) & df["Direccion"].notna()


def revisar(df, df_mercado=None):
    """
    Agrega a `df` una columna booleana por señal (`Senal_*`), la categoría
    automática (`Revision_Auto`: "Excluir", "Verificar" o "Sin observaciones")
    y el motivo (`Motivo_Auto`). Requiere Titulo, Descripcion, Barrio,
    Barrio_Oficial, Latitud, Longitud, Direccion, Precio_Valor y Ambientes.
    """
    out = df.copy()
    texto = _texto(out)
    titulo = out["Titulo"].fillna("").str.lower()

    excl = {k: texto.str.contains(p, regex=True) for k, p in PATRONES_EXCLUIR.items()}
    excl["Ubicacion_Inconsistente"], out["Distancia_Barrio_Declarado_km"] = \
        ubicacion_inconsistente(out, df_mercado)
    verif = {k: (titulo if k == "Uso_No_Residencial" else texto).str.contains(p, regex=True)
             for k, p in PATRONES_VERIFICAR.items()}
    verif["Posible_Duplicado"] = posibles_duplicados(out)

    for k, v in {**excl, **verif}.items():
        out[f"Senal_{k}"] = v.fillna(False).astype(bool)

    def motivos(fila, claves):
        return "; ".join(k.replace("_", " ").lower() for k in claves if fila[f"Senal_{k}"])

    m_excl = out.apply(lambda f: motivos(f, excl), axis=1)
    m_verif = out.apply(lambda f: motivos(f, verif), axis=1)
    out["Revision_Auto"] = np.where(m_excl != "", "Excluir",
                                    np.where(m_verif != "", "Verificar", "Sin observaciones"))
    out["Motivo_Auto"] = np.where(m_excl != "", m_excl, m_verif)
    return out
