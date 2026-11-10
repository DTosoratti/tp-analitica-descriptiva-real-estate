"""
Dashboard interactivo de oportunidades inmobiliarias.

Genera un único archivo HTML autocontenido (sin servidor ni librerías externas)
a partir de las bases del pipeline:
- data/processed/remax_deptos_features.csv  (notebook 03)
- data/processed/oportunidades_benchmark_ajustado.csv  (notebook 11)
- data/processed/flipping_modelo_economico.csv  (notebook 07)

Uso, desde la raíz del repositorio:
    python -m src.dashboard
y se abre dashboard/index.html en el navegador.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import (BASE_FEATURES, DESCUENTO_NEGOCIABLE_PCT, MARGEN_MINIMO_PCT,
                        PROCESSED_DIR, RAIZ, UMBRAL_GAP)

PLANTILLA = Path(__file__).resolve().parent / "dashboard_plantilla.html"
DESTINO = RAIZ / "dashboard" / "index.html"
PREFIJO_LINK = "https://www.remax.com.ar/listings/"


ESTADOS_PUBLICACION = {"active": "Activo", "reserved": "Reservado", "negotiation": "En negociación"}


def preparar_datos(features=BASE_FEATURES, oportunidades=PROCESSED_DIR / "oportunidades_benchmark_ajustado.csv",
                   ranking=PROCESSED_DIR / "ranking_visitas.csv"):
    """Une las bases y devuelve el DataFrame con las columnas que usa el dashboard."""
    feat = pd.read_csv(features)
    opor = pd.read_csv(oportunidades)
    d = opor.merge(
        feat[["ID", "Link", "Latitud", "Longitud", "Precio_Valor", "Superficie_Homogeneizada_m2",
              "Ambientes_Grupo", "Flag_Coordenadas_Invalidas", "Clasificacion_Oportunidad",
              "Estado_Publicacion"]],
        on="ID", how="left", validate="one_to_one")
    sin_geo = d["Flag_Coordenadas_Invalidas"].fillna(False).astype(bool) | d[["Latitud", "Longitud"]].isna().any(axis=1)
    d.loc[sin_geo, ["Latitud", "Longitud"]] = np.nan
    # Categoría: las unidades que necesitan obra se evalúan con el PER, no con este cruce
    d["Cat"] = d["Categoria_Doble"]
    d.loc[d["Estado_Propiedad"].eq("Necesita_obra"), "Cat"] = "Necesita_obra"
    # Baratas con indicadores de posible error de carga (no son candidatas de mayor confianza)
    d["Verif"] = d["Clasificacion_Oportunidad"].eq("Barata_requiere_verificacion")
    # Candidatas de mayor confianza: las del ranking de visitas revisado (notebook 09)
    visitas = pd.read_csv(ranking)
    d["Confianza"] = d["ID"].isin(visitas["ID"])
    automaticas = d["Categoria_Doble"].eq("Confirmada_por_ambos") & d["Clasificacion_Oportunidad"].eq("Barata")
    motivo = d["ID"].map(visitas.set_index("ID")["Motivo_Revision"])
    verificar = d["ID"].map(visitas.set_index("ID")["Revision"]).eq("Verificar")
    d["Revision"] = np.select(
        [d["Verif"], verificar, d["Confianza"], automaticas & ~d["Confianza"]],
        ["Requiere verificación (posible error de carga)",
         "Verificar",
         "Revisada",
         "Excluida (no comparable)"],
        default="–")
    d["Motivo_Revision"] = np.where(d["Verif"], "Indicadores de posible error de carga",
                                    motivo.fillna("").astype(str))
    d["Publicacion"] = d["Estado_Publicacion"].map(ESTADOS_PUBLICACION).fillna("Sin dato")
    return d


def preparar_flipping(flipping=PROCESSED_DIR / "flipping_modelo_economico.csv"):
    """Unidades que necesitan obra con su resultado económico (notebook 07)."""
    return pd.read_csv(flipping)


def _lista(serie, decimales=None):
    """Serie a lista JSON-compatible (NaN -> None)."""
    if decimales is not None:
        serie = serie.round(decimales)
    return [None if pd.isna(x) else (x.item() if hasattr(x, "item") else x) for x in serie]


def construir_json(d):
    link = d["Link"].map(lambda u: u[len(PREFIJO_LINK):] if isinstance(u, str) and u.startswith(PREFIJO_LINK) else u)
    columnas = {
        "barrio": _lista(d["Barrio_Oficial"]),
        "amb": _lista(d["Ambientes_Grupo"].astype(str)),
        "est": _lista(d["Estado_Propiedad"]),
        "cat": _lista(d["Cat"]),
        "precio": _lista(d["Precio_Valor"], 0),
        "sup": _lista(d["Superficie_Homogeneizada_m2"], 1),
        "usdm2": _lista(d["USD_m2_Homogeneizado"], 0),
        "bm": _lista(d["Benchmark_USD_m2"], 0),
        "gbm": _lista(d["Gap_Benchmark_pct"], 1),
        "ghed": _lista(d["Gap_Hedonico_pct"], 1),
        "lat": _lista(d["Latitud"], 5),
        "lon": _lista(d["Longitud"], 5),
        "link": _lista(link),
        "verif": _lista(d["Verif"]),
        "conf": _lista(d["Confianza"]),
        "rev": _lista(d["Revision"]),
        "revm": _lista(d["Motivo_Revision"]),
        "pub": _lista(d["Publicacion"]),
    }
    return {"n": len(d), "cols": list(columnas), "data": columnas}


def _link_corto(serie):
    return serie.map(lambda u: u[len(PREFIJO_LINK):] if isinstance(u, str) and u.startswith(PREFIJO_LINK) else u)


def construir_json_flipping(f):
    columnas = {
        "barrio": _lista(f["Barrio_Oficial"]),
        "amb": _lista(f["Ambientes_Grupo"].astype(str)),
        "sup": _lista(f["Superficie_Cubierta_m2"], 1),
        "nivel": _lista(f["Nivel_Obra"]),
        "precio": _lista(f["Precio_Valor"], 0),
        "pmax": _lista(f["Precio_Max_Oferta_USD"], 0),
        "desc": _lista(f["Descuento_Requerido_pct"], 1),
        "roic": _lista(f["ROI_Conservador_pct"], 1),
        "roib": _lista(f["ROI_Base_pct"], 1),
        "roio": _lista(f["ROI_Optimista_pct"], 1),
        "obra": _lista(f["Costo_Obra_Base_USD"], 0),
        "dec": _lista(f["Decision"]),
        "pub": _lista(f["Estado_Publicacion"].map(ESTADOS_PUBLICACION).fillna("Sin dato")),
        "alertas": _lista(f["Cantidad_Alertas"]),
        "link": _lista(_link_corto(f["Link"])),
    }
    return {"n": len(f), "cols": list(columnas), "data": columnas}


def generar_dashboard(destino=DESTINO):
    """Escribe el dashboard en `destino` y devuelve la ruta."""
    d = preparar_datos()
    f = preparar_flipping()
    meta = {
        "base": PREFIJO_LINK,
        "margen": MARGEN_MINIMO_PCT,
        "desc_neg": DESCUENTO_NEGOCIABLE_PCT,
        "gap": UMBRAL_GAP,
        "pie": (f"{len(d):,}".replace(",", ".") + " avisos de departamentos en venta de RE/MAX (corte de extracción aproximado: 26/09/2026), "
                "sin valores extremos ni ambientes dudosos. Son precios de publicación, no de cierre. "
                f"Brecha = % por debajo del precio esperado. Según el benchmark de comparables, barata = brecha de al menos {UMBRAL_GAP} % "
                f"y USD/m² en el cuartil inferior de sus comparables; según el benchmark ajustado, brecha de al menos {UMBRAL_GAP} %. "
                "Estado de publicación y links corresponden a la fecha de extracción: un aviso puede haberse vendido o dado de baja "
                "después, y en ese caso el link lleva a la página principal de RE/MAX. "
                "El benchmark ajustado controla antigüedad y características publicadas, pero no el estado del edificio, "
                "el piso ni las terminaciones: sirve para priorizar y contrastar, no para tasar. "
                f"Flipping: {len(f)} unidades que necesitan obra, con costos de obra, transacción, tenencia y costo de oportunidad "
                "según data/supuestos_flipping.csv (notebook 07); el precio máximo de oferta es el mayor precio al que el ROI base "
                f"es de al menos {MARGEN_MINIMO_PCT} %, el ROI conservador no es negativo y la brecha es de al menos {UMBRAL_GAP} %. Los costos de obra son supuestos con fuente secundaria, no cotizaciones."
                ),
    }
    html = (PLANTILLA.read_text(encoding="utf-8")
            .replace("/*DATOS*/null", json.dumps(construir_json(d), ensure_ascii=False, separators=(",", ":")))
            .replace("/*FLIP*/null", json.dumps(construir_json_flipping(f), ensure_ascii=False, separators=(",", ":")))
            .replace("/*META*/null", json.dumps(meta, ensure_ascii=False)))
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")
    return destino


if __name__ == "__main__":
    ruta = generar_dashboard()
    print("Dashboard generado:", ruta.relative_to(RAIZ), f"({ruta.stat().st_size / 1e6:.1f} MB)")
