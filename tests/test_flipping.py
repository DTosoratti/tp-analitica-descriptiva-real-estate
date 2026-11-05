"""
Tests del modelo económico de flipping (src/flipping.py) y de sus supuestos.

Ejecutar desde la raíz del repositorio:  python -m pytest tests/
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import flipping as fl
from src.config import MARGEN_MINIMO_PCT


def aviso(**kw):
    base = dict(ID=1, Titulo="Depto a reciclar", Descripcion="", A_Refaccionar=True,
                Barrio_Oficial="Caballito", Precio_Valor=100_000.0,
                Superficie_Cubierta_m2=50.0, Expensas_Imputadas=0.0,
                PER_Conservador=130_000.0, PER_Base=150_000.0, PER_Optimista=170_000.0,
                PER_N_Comparables=15, PER_Nivel=1, Flag_Senal_Contradictoria=False,
                Flag_Expensas_Imputadas=False)
    base.update(kw)
    return pd.DataFrame([base])


@pytest.fixture(scope="module")
def supuestos():
    return fl.cargar_supuestos()


def test_supuestos_completos_y_ordenados(supuestos):
    for esc in fl.ESCENARIOS:
        s = supuestos[esc]
        for comp in ["costo_obra_liviana", "costo_obra_media", "costo_obra_integral",
                     "contingencia", "costos_compra", "costos_venta",
                     "plazo_comercializacion", "tasa_oportunidad"]:
            assert comp in s, f"falta {comp} en {esc}"
        assert s["costo_obra_liviana"] < s["costo_obra_media"] < s["costo_obra_integral"]
        assert 0 <= s["costos_compra"] < 1 and 0 <= s["costos_venta"] < 1
    # El conservador nunca es más barato que el optimista
    assert supuestos["Conservador"]["costo_obra_integral"] >= supuestos["Optimista"]["costo_obra_integral"]


def test_nivel_obra_segun_texto():
    df = pd.concat([
        aviso(Titulo="Depto a reciclar", A_Refaccionar=True),
        aviso(Titulo="Depto para actualizar", A_Refaccionar=False),
        aviso(Titulo="Depto", A_Refaccionar=False),
    ], ignore_index=True)
    nivel, evidencia = fl.asignar_nivel_obra(df)
    assert list(nivel) == ["Integral", "Media", "Integral"]
    assert list(evidencia) == ["Señal fuerte", "Señal débil", "Sin evidencia"]


def test_formula_roi_escenario_base(supuestos):
    df = aviso().assign(Nivel_Obra="Media")
    r = fl.calcular_escenarios(df, supuestos, premium=set()).iloc[0]
    s = supuestos["Base"]
    meses = s["plazo_obra_media"] + s["plazo_comercializacion"]
    obra = 50 * s["costo_obra_media"] * (1 + s["contingencia"])
    capital = 100_000 * (1 + s["costos_compra"]) + obra
    inversion = capital * (1 + s["tasa_oportunidad"] * meses / 12)
    roi = (150_000 * (1 - s["costos_venta"]) - inversion) / inversion * 100
    assert r["ROI_Base_pct"] == pytest.approx(roi)


def test_precio_maximo_deja_el_margen_minimo(supuestos):
    df = aviso().assign(Nivel_Obra="Media")
    r = fl.calcular_escenarios(df, supuestos, premium=set()).iloc[0]
    pmax = r["Precio_Max_Oferta_Base_USD"]
    r2 = fl.calcular_escenarios(df.assign(Precio_Valor=pmax), supuestos, premium=set()).iloc[0]
    assert r2["ROI_Base_pct"] == pytest.approx(MARGEN_MINIMO_PCT, abs=1e-6)


def test_premium_encarece_la_obra(supuestos):
    df = aviso().assign(Nivel_Obra="Integral")
    normal = fl.calcular_escenarios(df, supuestos, premium=set()).iloc[0]
    caro = fl.calcular_escenarios(df, supuestos, premium={"Caballito"}).iloc[0]
    assert caro["Costo_Obra_Conservador_USD"] > normal["Costo_Obra_Conservador_USD"]


def test_descuento_de_compra_mejora_el_roi(supuestos):
    df = aviso().assign(Nivel_Obra="Media")
    sin = fl.calcular_escenarios(df, supuestos, premium=set()).iloc[0]
    con = fl.calcular_escenarios(df, supuestos, premium=set(), descuento_compra=0.1).iloc[0]
    assert con["ROI_Base_pct"] > sin["ROI_Base_pct"]


def test_regla_de_decision():
    df = pd.DataFrame({
        "PER_N_Comparables": [15, 15, 15, 5],
        "Inversion_Total_Base_USD": [100_000] * 4,
        "Cantidad_Alertas": [0, 0, 1, 0],
        "ROI_Base_pct": [20, 5, 20, 20],
        "ROI_Conservador_pct": [1, -5, 1, 1],
        "Descuento_Requerido_Base_pct": [-3, 8, -3, -3],
    })
    assert list(fl.aplicar_regla(df, margen=15, descuento_max=10)) == [
        "Comprar al precio publicado", "Ofertar con descuento",
        "Revisar manualmente", "Descartar"]
