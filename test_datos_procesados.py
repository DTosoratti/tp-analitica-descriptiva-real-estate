"""
Controles de consistencia sobre los datos procesados versionados.

Verifican que los archivos de data/processed/ correspondan a la misma versión
del análisis (criterio de trazabilidad de la consigna). Si un notebook se
vuelve a correr y algún control falla, hay que revisar el cambio antes de
subirlo.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.config import BASE_FEATURES, BASE_LIMPIA, PROCESSED_DIR, UMBRAL_GAP
from src.patrones import clasificar_estado


@pytest.fixture(scope="module")
def features():
    return pd.read_csv(BASE_FEATURES)


def test_base_limpia_sin_duplicados():
    limpia = pd.read_csv(BASE_LIMPIA, usecols=["ID"])
    assert len(limpia) == 9_500
    assert limpia["ID"].is_unique


def test_clasificacion_respeta_umbral_de_gap(features):
    baratas = features[features["Clasificacion_Oportunidad"].eq("Barata")]
    assert (baratas["Gap_Subvaluacion_pct"] >= UMBRAL_GAP).all()
    assert not baratas["Estado_Propiedad"].eq("Necesita_obra").any()


def test_per_ordenado_por_escenario(features):
    per = features.dropna(subset=["PER_Base"])
    assert (per["PER_Conservador"] <= per["PER_Base"]).all()
    assert (per["PER_Base"] <= per["PER_Optimista"]).all()


def test_flipping_consistente_con_features(features):
    flip = pd.read_csv(PROCESSED_DIR / "flipping_modelo_economico.csv")
    evaluables = features["Precio_Valor"].gt(0) & features["PER_Base"].gt(0) & features["Superficie_Cubierta_m2"].gt(0)
    assert len(flip) == evaluables.sum()
    assert flip["ID"].is_unique
    assert set(flip["ID"]) <= set(features["ID"])


def test_ranking_visitas_solo_confirmadas():
    rv = pd.read_csv(PROCESSED_DIR / "ranking_visitas.csv")
    assert rv["ID"].is_unique
    assert (rv["Gap_Hedonico_pct"] > 0).all() and (rv["Gap_Benchmark_pct"] >= UMBRAL_GAP).all()


@pytest.mark.parametrize("texto, esperado", [
    ("departamento a reciclar en caballito", "Necesita_obra"),
    ("excelente estado, muy luminoso", "Buen_estado"),
    ("departamento de 3 ambientes", "Sin_clasificar"),
])
def test_clasificador_de_estado(texto, esperado):
    assert clasificar_estado(pd.Series([texto]))[0] == esperado
