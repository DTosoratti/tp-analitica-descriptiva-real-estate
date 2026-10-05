"""
Funciones de diagnóstico usadas en la limpieza de la base RE/MAX CABA.

- ambientes_desde_titulo: extrae la cantidad de ambientes declarada en el título.
- normalizar_etiqueta: unifica la escritura de etiquetas de texto (para compararlas).
- diagnostico_faltantes / logit_faltantes: diagnóstico del mecanismo de faltantes
  (MCAR / MAR) comparando avisos con y sin dato.
- detectar_outliers: Box-Cox + Tukey por variable y distancia de Mahalanobis.
"""

import re
import unicodedata

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from scipy.stats import boxcox, chi2


# TEXTO


NUMEROS_PALABRA = {"un": 1, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4,
                   "cinco": 5, "seis": 6, "siete": 7}


def ambientes_desde_titulo(titulo):
    """Cantidad de ambientes que declara el título del aviso (NaN si no la declara)."""
    t = str(titulo).lower()
    if re.search(r"mono\s?amb", t):
        return 1
    m = re.search(r"\b(\d{1,2})\s*amb", t)
    if m:
        return int(m.group(1))
    m = re.search(r"\b(un|uno|dos|tres|cuatro|cinco|seis|siete)\s+amb", t)
    if m:
        return NUMEROS_PALABRA[m.group(1)]
    return np.nan


def normalizar_etiqueta(texto):
    """Minúsculas, sin acentos y sin espacios repetidos (solo para comparar escrituras)."""
    if pd.isna(texto):
        return texto
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode("ascii")
    return " ".join(t.lower().split())


# VALORES FALTANTES


def diagnostico_faltantes(df, variable, numericas, categoricas):
    """
    Compara los avisos con y sin dato en `variable`.

    - Numéricas: test t de Welch (H0: medias iguales en ambos grupos).
    - Categóricas: test chi-cuadrado (H0: el faltante es independiente de la categoría).
    """
    falta = df[variable].isna()
    filas = []
    for col in numericas:
        con_dato = df.loc[~falta, col].dropna()
        sin_dato = df.loc[falta, col].dropna()
        _, p = stats.ttest_ind(con_dato, sin_dato, equal_var=False)
        filas.append({"Variable": col, "Test": "t de Welch",
                      "Media con dato": round(con_dato.mean(), 3),
                      "Media sin dato": round(sin_dato.mean(), 3),
                      "p-valor": p})
    for col in categoricas:
        tabla = pd.crosstab(df[col], falta)
        _, p, _, _ = stats.chi2_contingency(tabla)
        filas.append({"Variable": col, "Test": "Chi-cuadrado", "p-valor": p})
    resultado = pd.DataFrame(filas).set_index("Variable")
    resultado["Rechaza H0 (5%)"] = resultado["p-valor"] < 0.05
    return resultado


def logit_faltantes(df, variable, numericas):
    """Regresión logística del indicador de faltante de `variable` sobre `numericas`."""
    y = df[variable].isna().astype(int)
    X = sm.add_constant(df[numericas])
    modelo = sm.Logit(y, X, missing="drop").fit(disp=0)
    return modelo.summary2().tables[1][["Coef.", "P>|z|"]].round(4)


# OUTLIERS


def detectar_outliers(df, variables,
                      vars_mahalanobis=("Precio_m2_Total", "Superficie_Total_m2"),
                      extra_mahalanobis=("Ambientes",),
                      nivel=0.975):
    """
    Detección de outliers.

    Para cada variable de `variables`: transformación Box-Cox y regla de Tukey
    (atípico: fuera de 1,5 IQR; extremo: fuera de 3 IQR) sobre la variable transformada.

    Multivariado: distancia de Mahalanobis² sobre las variables de `vars_mahalanobis`
    (transformadas) y las de `extra_mahalanobis` (sin transformar), con umbral dado
    por el percentil `nivel` de una chi-cuadrado.

    Devuelve un DataFrame con el mismo índice que `df`.
    """
    res = pd.DataFrame(index=df.index)
    for var in variables:
        transformada, _ = boxcox(df[var])
        transformada = pd.Series(transformada, index=df.index)
        res[f"bc_{var}"] = transformada
        q1, q3 = transformada.quantile([0.25, 0.75])
        iqr = q3 - q1
        res[f"atipico_bajo_{var}"] = transformada < q1 - 1.5 * iqr
        res[f"atipico_alto_{var}"] = transformada > q3 + 1.5 * iqr
        res[f"extremo_{var}"] = (transformada < q1 - 3 * iqr) | (transformada > q3 + 3 * iqr)

    columnas = [res[f"bc_{v}"] for v in vars_mahalanobis] + [df[v] for v in extra_mahalanobis]
    X = np.column_stack(columnas)
    diferencia = X - X.mean(axis=0)
    inv_cov = np.linalg.inv(np.cov(X, rowvar=False))
    res["mahalanobis2"] = np.einsum("ij,jk,ik->i", diferencia, inv_cov, diferencia)
    res["outlier_mahal"] = res["mahalanobis2"] > chi2.ppf(nivel, df=X.shape[1])
    return res
