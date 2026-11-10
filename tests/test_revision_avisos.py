"""
Tests de la revisión de la lista de visitas (src/revision_avisos.py).

Ejecutar desde la raíz del repositorio:  python -m pytest tests/
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import revision_avisos as rv
from src.config import DATA_DIR, PROCESSED_DIR


def aviso(**kw):
    base = dict(ID=1, Titulo="Depto 2 ambientes", Descripcion="Luminoso, al frente.",
                Barrio="Palermo", Barrio_Oficial="Palermo", Latitud=-34.585, Longitud=-58.42,
                Direccion="Calle 100", Precio_Valor=100_000.0, Ambientes=2)
    base.update(kw)
    return base


def mercado():
    # Centros aproximados de dos barrios
    return pd.DataFrame([aviso(ID=10 + i) for i in range(3)]
                        + [aviso(ID=20 + i, Barrio="Balvanera", Barrio_Oficial="Balvanera",
                                 Latitud=-34.607, Longitud=-58.405) for i in range(3)])


def test_senales_de_texto():
    df = pd.DataFrame([
        aviso(ID=1, Descripcion="PRECIO PUBLICADO ES DEL ANTICIPO DEL 50%."),
        aviso(ID=2, Titulo="Venta de nuda propiedad 2 ambientes"),
        aviso(ID=3, Descripcion="Por escritura, la unidad funcional consta como cochera."),
        aviso(ID=4, Titulo="Oficina en venta"),
        aviso(ID=5, Descripcion="Se vende con contrato de alquiler vigente hasta 2027."),
        aviso(ID=6),
    ])
    df["Direccion"] = [f"Calle {i}" for i in range(len(df))]
    r = rv.revisar(df, mercado()).set_index("ID")
    assert list(r["Revision_Auto"]) == ["Excluir", "Excluir", "Excluir", "Verificar", "Verificar",
                                        "Sin observaciones"]


def test_ubicacion_inconsistente():
    # Declara Balvanera pero las coordenadas caen en Núñez (lejos del centro de Balvanera)
    lejos = aviso(ID=1, Barrio="Balvanera", Barrio_Oficial="Nuñez", Latitud=-34.545, Longitud=-58.46)
    # Declara Barrio Norte (informal) y cae en Recoleta: no es error
    informal = aviso(ID=2, Barrio="Barrio Norte", Barrio_Oficial="Recoleta")
    m = pd.concat([mercado(), pd.DataFrame([aviso(ID=30, Barrio="Recoleta", Barrio_Oficial="Recoleta")])])
    flag, _ = rv.ubicacion_inconsistente(pd.DataFrame([lejos, informal]), m)
    assert list(flag) == [True, False]


def test_ranking_exportado_sin_excluidos():
    """Ningún aviso excluido en la revisión manual queda en el ranking de visitas."""
    rank = pd.read_csv(PROCESSED_DIR / "ranking_visitas.csv")
    manual = pd.read_csv(DATA_DIR / "validation" / "revision_lista_visitas.csv")
    excluidos = set(manual.loc[manual["Decision_Manual"].eq("Excluir"), "ID"])
    assert excluidos and not excluidos & set(rank["ID"])
    assert rank["Ranking_Visita"].tolist() == list(range(1, len(rank) + 1))
    for id_ in [654884, 568677, 582968, 353262]:   # anticipo, nuda propiedad, cochera, ubicación
        assert id_ not in set(rank["ID"])


def test_posible_duplicado():
    df = pd.DataFrame([aviso(ID=1), aviso(ID=2), aviso(ID=3, Direccion="Otra 1")])
    assert list(rv.posibles_duplicados(df)) == [True, True, False]
