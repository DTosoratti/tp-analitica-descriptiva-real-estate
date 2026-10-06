"""
Funciones auxiliares para el análisis exploratorio (notebook 04).

- resumen_robusto: estadísticos de resumen de variables numéricas.
- dispersion_por_grupo: mediana, cuartiles y dispersión relativa por grupo.
- test_mann_whitney: comparación de dos grupos (no paramétrica).
- test_kruskal: comparación de k grupos (no paramétrica).
- premio_por_variable: diferencia de una métrica entre avisos con y sin una característica.
"""

import numpy as np
import pandas as pd
from scipy import stats


def resumen_robusto(df, columnas):
    """Media, mediana, desvío, asimetría, curtosis y cuantiles de cada columna."""
    filas = []
    for col in columnas:
        x = df[col].dropna()
        filas.append({
            "Variable": col,
            "N": len(x),
            "Media": x.mean(),
            "Mediana": x.median(),
            "Desvío": x.std(),
            "Asimetría": stats.skew(x),
            "Curtosis": stats.kurtosis(x),
            "P05": x.quantile(0.05),
            "P25": x.quantile(0.25),
            "P75": x.quantile(0.75),
            "P95": x.quantile(0.95),
        })
    return pd.DataFrame(filas).set_index("Variable").round(2)


def dispersion_por_grupo(df, grupo, valor, min_n=30):
    """
    Mediana, P25, P75, IQR y dispersión relativa (IQR / mediana) de `valor`
    por `grupo`. Solo se informan los grupos con al menos `min_n` casos.
    """
    tabla = (
        df.groupby(grupo, observed=True)[valor]
        .agg(N="count", Mediana="median",
             P25=lambda x: x.quantile(0.25), P75=lambda x: x.quantile(0.75))
    )
    tabla["IQR"] = tabla["P75"] - tabla["P25"]
    tabla["Dispersion_relativa"] = tabla["IQR"] / tabla["Mediana"]
    return tabla.loc[tabla["N"] >= min_n].sort_values("Mediana", ascending=False).round(3)


def test_mann_whitney(x, y, nombre_x, nombre_y, alternativa="two-sided", diferencia="porcentual"):
    """
    Test U de Mann-Whitney entre dos grupos.
    H0: las distribuciones de ambos grupos son iguales.
    H1 según `alternativa`: 'less' (x tiende a ser menor que y),
    'greater' (x tiende a ser mayor) o 'two-sided' (difieren).
    `diferencia`: 'porcentual' (para niveles, como USD/m²) o 'puntos'
    (para variables que ya están en %, como el precio relativo).
    """
    x, y = pd.Series(x).dropna(), pd.Series(y).dropna()
    u, p = stats.mannwhitneyu(x, y, alternative=alternativa)
    return pd.Series({
        f"N {nombre_x}": len(x),
        f"N {nombre_y}": len(y),
        f"Mediana {nombre_x}": round(x.median(), 2),
        f"Mediana {nombre_y}": round(y.median(), 2),
        ("Diferencia de medianas (%)" if diferencia == "porcentual" else "Diferencia de medianas (puntos)"):
            round((x.median() / y.median() - 1) * 100 if diferencia == "porcentual"
                  else x.median() - y.median(), 1),
        "Estadístico U": round(u, 1),
        "p-valor": p,
        "Rechaza H0 (5%)": p < 0.05,
    })


def test_kruskal(df, grupo, valor, min_n=10):
    """
    Test de Kruskal-Wallis entre los grupos con al menos `min_n` casos.
    H0: la distribución de `valor` es la misma en todos los grupos.
    """
    grupos = [g[valor].dropna() for _, g in df.groupby(grupo, observed=True)
              if g[valor].notna().sum() >= min_n]
    h, p = stats.kruskal(*grupos)
    return pd.Series({"Grupos comparados": len(grupos), "Estadístico H": round(h, 2),
                      "p-valor": p, "Rechaza H0 (5%)": p < 0.05})


def premio_por_variable(df, variables, metrica):
    """
    Para cada variable booleana, compara `metrica` entre avisos con y sin la
    característica (mediana de cada grupo, diferencia y test de Mann-Whitney
    bilateral).
    """
    filas = []
    for var in variables:
        con = df.loc[df[var].astype(bool), metrica].dropna()
        sin = df.loc[~df[var].astype(bool), metrica].dropna()
        _, p = stats.mannwhitneyu(con, sin, alternative="two-sided")
        filas.append({
            "Variable": var,
            "N con": len(con),
            "Mediana con": con.median(),
            "Mediana sin": sin.median(),
            "Diferencia (puntos)": con.median() - sin.median(),
            "p-valor": p,
            "Rechaza H0 (5%)": p < 0.05,
        })
    return (pd.DataFrame(filas).set_index("Variable")
            .sort_values("Diferencia (puntos)", ascending=False).round(3))
