"""
Tests del dashboard (src/dashboard.py): las cifras que muestra deben coincidir
con las de las notebooks 07 y 09.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import PROCESSED_DIR
from src.dashboard import construir_json, construir_json_flipping, preparar_datos, preparar_flipping


def test_candidatas_coinciden_con_ranking_de_visitas():
    d = preparar_datos()
    rv = pd.read_csv(PROCESSED_DIR / "ranking_visitas.csv")
    assert set(d.loc[d["Confianza"], "ID"]) == set(rv["ID"])


def test_flipping_coincide_con_modelo_economico():
    f = preparar_flipping()
    base = pd.read_csv(PROCESSED_DIR / "flipping_modelo_economico.csv")
    assert len(f) == len(base)
    assert (f["ROI_Conservador_pct"] > 0).sum() == (base["ROI_Conservador_pct"] > 0).sum()


def test_json_columnas_del_mismo_largo():
    for js in (construir_json(preparar_datos()), construir_json_flipping(preparar_flipping())):
        assert all(len(v) == js["n"] for v in js["data"].values())


def test_baratas_del_dashboard_cumplen_la_definicion_que_muestra():
    """Barata según el benchmark = brecha ≥ umbral y USD/m² ≤ P25 de los comparables."""
    from src.config import BASE_FEATURES, UMBRAL_GAP
    d = preparar_datos().merge(
        pd.read_csv(BASE_FEATURES, usecols=["ID", "P25_USD_m2_Comparable"]), on="ID")
    b = d[d["Cat"].isin(["Confirmada_por_ambos", "Solo_benchmark"])]
    assert (b["Gap_Benchmark_pct"] >= UMBRAL_GAP).all()
    assert (b["USD_m2_Homogeneizado"] <= b["P25_USD_m2_Comparable"]).all()
    a = d[d["Cat"].isin(["Confirmada_por_ambos", "Solo_hedonico"])]
    assert (a["Gap_Hedonico_pct"] >= UMBRAL_GAP).all()


def test_estado_de_publicacion_informado():
    d = preparar_datos()
    assert d["Publicacion"].isin(["Activo", "Reservado", "En negociación", "Sin dato"]).all()
    assert (d["Publicacion"] != "Sin dato").mean() > 0.99
