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
