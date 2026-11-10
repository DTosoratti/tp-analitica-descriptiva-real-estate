"""
Modelo explicativo del precio por m² (regresión hedónica) y su validación.

- preparar_base_modelo: selecciona avisos y construye las variables del modelo.
- ajustar_hedonico: regresión de log(USD/m² homogeneizado) con errores robustos.
- tabla_efectos: efecto porcentual de cada variable, con intervalo de confianza.
- validar_fuera_de_muestra: holdout repetido contra el benchmark jerárquico.
- vif_por_termino / diagnostico_residuos: colinealidad y supuestos del modelo.

El coeficiente de una variable indica la diferencia porcentual del USD/m²
asociada a esa característica, controlando por las demás. Es una asociación,
no una relación causal.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

CARACTERISTICAS = [
    "Pileta", "SUM", "Gimnasio", "Seguridad", "Laundry", "Parrilla", "Solarium",
    "Ascensor", "Baulera", "Balcon", "Terraza", "Patio", "Cochera_Incluida",
    "Luminoso", "Vista", "Silencioso", "Contrafrente", "Al_Frente",
    "Apto_Profesional",
]

ESTADOS = ["Buen_estado", "Reciclada_refaccionada", "Necesita_obra", "Sin_clasificar"]

FORMULA = (
    "ln_usd_m2 ~ C(Barrio_Oficial) + C(Ambientes_Grupo, Treatment('1')) + ln_sup"
    " + C(Banda_Antiguedad, Treatment('11_30')) + "
    + " + ".join(CARACTERISTICAS)
    + " + Reciclado_Parcial + C(Estado, Treatment('Buen_estado'))"
)


def preparar_base_modelo(df):
    """Avisos sin valores extremos ni ambientes dudosos, con las variables del modelo."""
    d = df[
        (~df["Flag_Extremo"])
        & (~df["Flag_Ambientes_Dudoso"])
        & df["USD_m2_Homogeneizado"].notna()
        & df["Barrio_Oficial"].notna()
    ].copy()
    d["ln_usd_m2"] = np.log(d["USD_m2_Homogeneizado"])
    d["ln_sup"] = np.log(d["Superficie_Homogeneizada_m2"])
    for col in CARACTERISTICAS + ["Reciclado_Parcial"]:
        d[col] = d[col].fillna(False).astype(int)
    d["Estado"] = pd.Categorical(d["Estado_Propiedad"], categories=ESTADOS)
    return d


def ajustar_hedonico(d, robusto=True):
    """Ajusta la regresión; con `robusto` usa errores estándar HC3."""
    modelo = smf.ols(FORMULA, data=d)
    return modelo.fit(cov_type="HC3") if robusto else modelo.fit()


def _etiqueta(nombre):
    if nombre.startswith("C(Estado"):
        return "Estado: " + nombre.split("T.")[1].rstrip("]")
    if nombre.startswith("C(Banda_Antiguedad"):
        return "Antigüedad: " + nombre.split("T.")[1].rstrip("]")
    if nombre.startswith("C(Ambientes_Grupo"):
        return "Ambientes: " + nombre.split("T.")[1].rstrip("]")
    return nombre


def tabla_efectos(modelo):
    """Efecto porcentual (exp(b) - 1) de cada variable, con IC al 95 % y p-valor."""
    ic = modelo.conf_int()
    filas = []
    for nombre in modelo.params.index:
        if nombre == "Intercept" or nombre.startswith("C(Barrio_Oficial"):
            continue
        b = modelo.params[nombre]
        filas.append({
            "Variable": _etiqueta(nombre),
            "Efecto (%)": (np.exp(b) - 1) * 100,
            "IC95 inf.": (np.exp(ic.loc[nombre, 0]) - 1) * 100,
            "IC95 sup.": (np.exp(ic.loc[nombre, 1]) - 1) * 100,
            "p-valor": modelo.pvalues[nombre],
        })
    return pd.DataFrame(filas).set_index("Variable")


def _mape(pred, real):
    err = (pred - real).abs() / real * 100
    return err.mean(), err.median()


def validar_fuera_de_muestra(d, semillas=(1, 2, 3, 4, 5), prop_prueba=0.2):
    """
    Holdout repetido: ajusta el modelo con el (1 - prop_prueba) de los avisos y
    lo compara, en el resto, con el benchmark jerárquico (`Benchmark_USD_m2`).
    Devuelve MAPE y MdAPE de ambos por semilla, sobre los mismos avisos.
    """
    filas = []
    for semilla in semillas:
        rng = np.random.RandomState(semilla)
        orden = rng.permutation(len(d))
        corte = int((1 - prop_prueba) * len(d))
        train, test = d.iloc[orden[:corte]], d.iloc[orden[corte:]]
        test = test[test["Barrio_Oficial"].isin(train["Barrio_Oficial"].unique())]
        test = test.dropna(subset=["Benchmark_USD_m2"])
        modelo = smf.ols(FORMULA, data=train).fit()
        pred = np.exp(modelo.predict(test)) * np.exp(modelo.scale / 2)
        real = test["USD_m2_Homogeneizado"]
        mape_r, mdape_r = _mape(pred, real)
        mape_b, mdape_b = _mape(test["Benchmark_USD_m2"], real)
        filas.append({"Semilla": semilla, "N prueba": len(test),
                      "MAPE regresión (%)": mape_r, "MdAPE regresión (%)": mdape_r,
                      "MAPE benchmark (%)": mape_b, "MdAPE benchmark (%)": mdape_b})
    return pd.DataFrame(filas).set_index("Semilla")


def efecto_necesita_obra(d, formula=None):
    """Efecto porcentual de `Necesita_obra` (frente a `Buen_estado`) con su IC al 95 %."""
    d = d.copy()
    d["Estado"] = d["Estado"].cat.remove_unused_categories()
    modelo = smf.ols(formula or FORMULA, data=d).fit(cov_type="HC3")
    nombre = [k for k in modelo.params.index if "Necesita_obra" in k][0]
    ic = modelo.conf_int().loc[nombre]
    return {"N": len(d),
            "Efecto (%)": (np.exp(modelo.params[nombre]) - 1) * 100,
            "IC95 inf.": (np.exp(ic[0]) - 1) * 100,
            "IC95 sup.": (np.exp(ic[1]) - 1) * 100}


def diferencia_obra_vs_reciclada(modelo):
    """Diferencia porcentual del USD/m² de `Necesita_obra` frente a `Reciclada_refaccionada`."""
    nombres = list(modelo.params.index)
    a = [k for k in nombres if "Necesita_obra" in k][0]
    b = [k for k in nombres if "Reciclada_refaccionada" in k][0]
    contraste = np.zeros(len(nombres))
    contraste[nombres.index(a)], contraste[nombres.index(b)] = 1, -1
    t = modelo.t_test(contraste)
    ef, (lo, hi) = float(t.effect[0]), t.conf_int()[0]
    return (np.exp(ef) - 1) * 100, (np.exp(lo) - 1) * 100, (np.exp(hi) - 1) * 100


# DIAGNÓSTICO DEL MODELO: COLINEALIDAD Y RESIDUOS
# Las funciones reciben la matriz de diseño y los residuos del modelo ajustado
# (modelo.model.exog, modelo.model.exog_names, modelo.resid, modelo.fittedvalues)
# y solo usan numpy y scipy.


def _termino(nombre):
    """Término de la fórmula al que pertenece una columna de la matriz de diseño."""
    return nombre.split("[")[0] if nombre.startswith("C(") else nombre


def vif_por_termino(exog, nombres):
    """
    Factor de inflación de la varianza por término.

    Para variables de una sola columna es el VIF clásico, 1 / (1 − R²_j). Para
    las categóricas con varias columnas (barrio, ambientes, antigüedad, estado),
    el VIF de cada dummy no es interpretable, así que se usa el VIF generalizado
    (GVIF) de Fox y Monette (1992):

        GVIF = det(R_11) · det(R_22) / det(R)

    con R la matriz de correlación de las columnas sin intercepto, R_11 la del
    término y R_22 la del resto. Para comparar términos con distintos grados de
    libertad (gl) se informa GVIF^(1 / (2 gl)), que para gl = 1 es la raíz del
    VIF clásico (regla habitual: preocupa por encima de √5 ≈ 2,2 o √10 ≈ 3,2).
    """
    X = pd.DataFrame(np.asarray(exog, dtype=float), columns=list(nombres))
    X = X.drop(columns=[c for c in X.columns if c == "Intercept"])
    X = X.loc[:, X.std() > 0]
    R = np.corrcoef(X.to_numpy(), rowvar=False)
    _, logdet_total = np.linalg.slogdet(R)
    terminos = pd.Series([_termino(c) for c in X.columns], index=X.columns)
    filas = []
    for term, cols in terminos.groupby(terminos, sort=False):
        idx = np.flatnonzero(terminos.index.isin(cols.index))
        resto = np.setdiff1d(np.arange(len(X.columns)), idx)
        _, ld1 = np.linalg.slogdet(R[np.ix_(idx, idx)])
        _, ld2 = np.linalg.slogdet(R[np.ix_(resto, resto)])
        gvif = float(np.exp(ld1 + ld2 - logdet_total))
        gl = len(idx)
        filas.append({"Término": _etiqueta(term) if gl == 1 else term, "gl": gl,
                      "GVIF": gvif, "GVIF^(1/(2gl))": gvif ** (1 / (2 * gl))})
    return pd.DataFrame(filas).set_index("Término").sort_values("GVIF^(1/(2gl))", ascending=False)


def diagnostico_residuos(resid, ajustados, exog):
    """
    Pruebas sobre los residuos del modelo:

    - normalidad: asimetría, curtosis y Jarque-Bera;
    - heterocedasticidad: Breusch-Pagan (regresión de los residuos al cuadrado
      sobre los regresores; LM = n · R²) y la correlación de Spearman entre
      |residuo| y el valor ajustado;
    - observaciones influyentes: residuos estudentizados internos con |r| > 3 y
      distancia de Cook > 4 / n, a partir de la diagonal de la matriz sombrero.

    Devuelve (resumen, detalle por aviso).
    """
    e = np.asarray(resid, dtype=float)
    yhat = np.asarray(ajustados, dtype=float)
    X = np.asarray(exog, dtype=float)
    n, k = X.shape

    jb = stats.jarque_bera(e)
    e2 = e ** 2
    coef, *_ = np.linalg.lstsq(X, e2, rcond=None)
    r2_aux = 1 - ((e2 - X @ coef) ** 2).sum() / ((e2 - e2.mean()) ** 2).sum()
    rango = np.linalg.matrix_rank(X)
    lm_bp = n * r2_aux
    p_bp = stats.chi2.sf(lm_bp, rango - 1)
    rho_het, p_het = stats.spearmanr(np.abs(e), yhat)

    Q, _ = np.linalg.qr(X)
    h = (Q ** 2).sum(axis=1)
    s2 = (e2.sum()) / (n - rango)
    r_est = e / np.sqrt(s2 * (1 - h))
    cook = r_est ** 2 * h / (rango * (1 - h))

    resumen = pd.Series({
        "N": n,
        "Asimetría": stats.skew(e),
        "Curtosis (exceso)": stats.kurtosis(e),
        "Jarque-Bera": jb.statistic, "Jarque-Bera p-valor": jb.pvalue,
        "Breusch-Pagan LM": lm_bp, "Breusch-Pagan p-valor": p_bp,
        "Spearman |residuo| vs. ajustado": rho_het,
        "% residuos estudentizados |r| > 3": np.mean(np.abs(r_est) > 3) * 100,
        "% con distancia de Cook > 4/n": np.mean(cook > 4 / n) * 100,
        "Distancia de Cook máxima": cook.max(),
    })
    detalle = pd.DataFrame({"Residuo": e, "Ajustado": yhat, "Leverage": h,
                            "Residuo_Estudentizado": r_est, "Cook": cook},
                           index=getattr(resid, "index", None))
    return resumen, detalle


# BENCHMARK AJUSTADO POR CARACTERÍSTICAS (predicción fuera de muestra)

def prediccion_cruzada(d, k=5, semilla=7):
    """
    Predicción fuera de muestra (validación cruzada de `k` pliegues) del USD/m²
    esperado de cada aviso con la regresión hedónica.

    Cada aviso se predice con un modelo que no lo vio al ajustarse, de modo que
    las brechas calculadas no están infladas por sobreajuste.

    Agrega a una copia de `d`:
    - Pred_USD_m2_Propio: USD/m² esperado dado el estado actual del aviso.
    - Pred_USD_m2_Reciclado: USD/m² esperado si el aviso estuviera reciclado
      (`Estado` = Reciclada_refaccionada, `Reciclado_Parcial` = 0).
    Los avisos de barrios ausentes en el conjunto de ajuste quedan en NaN.
    """
    d = d.copy()
    pliegue = np.random.RandomState(semilla).permutation(len(d)) % k
    d["Pred_USD_m2_Propio"] = np.nan
    d["Pred_USD_m2_Reciclado"] = np.nan
    for i in range(k):
        entrenamiento, prueba = d[pliegue != i], d[pliegue == i]
        prueba = prueba[prueba["Barrio_Oficial"].isin(entrenamiento["Barrio_Oficial"].unique())]
        modelo = smf.ols(FORMULA, data=entrenamiento).fit()
        correccion = np.exp(modelo.scale / 2)   # de la media del log a la media del nivel
        d.loc[prueba.index, "Pred_USD_m2_Propio"] = np.exp(modelo.predict(prueba)) * correccion
        reciclada = prueba.copy()
        reciclada["Estado"] = pd.Categorical(["Reciclada_refaccionada"] * len(reciclada),
                                             categories=prueba["Estado"].cat.categories)
        reciclada["Reciclado_Parcial"] = 0
        d.loc[prueba.index, "Pred_USD_m2_Reciclado"] = np.exp(modelo.predict(reciclada)) * correccion
    return d


def comparar_precision(d, columnas_pred):
    """MAPE y MdAPE (%) de cada predicción de `columnas_pred` ({nombre: columna}) frente al USD/m² observado."""
    filas = {}
    for nombre, col in columnas_pred.items():
        mape, mdape = _mape(d[col], d["USD_m2_Homogeneizado"])
        filas[nombre] = {"N": int(d[col].notna().sum()), "MAPE (%)": mape, "MdAPE (%)": mdape}
    return pd.DataFrame(filas).T


def clasificar_barata_doble(d, umbral_gap=25):
    """
    Cruza la brecha del benchmark jerárquico con la brecha hedónica (ambas en %
    por debajo de lo esperado) para los avisos que no necesitan obra.

    Categorías: Confirmada_por_ambos, Solo_benchmark (el descuento se explica por
    antigüedad y características), Solo_hedonico, No_barata.

    Del lado del benchmark jerárquico se aplica la definición completa de
    "barata" del proyecto (`src/benchmark.py`): brecha ≥ umbral **y** USD/m² en
    el cuartil inferior de los comparables (≤ `P25_USD_m2_Comparable`). Del lado
    del benchmark ajustado no hay grupo de comparables, así que se usa solo la
    brecha ≥ umbral.
    """
    d = d.copy()
    d["Gap_Benchmark_pct"] = (d["Benchmark_USD_m2"] - d["USD_m2_Homogeneizado"]) / d["Benchmark_USD_m2"] * 100
    d["Gap_Hedonico_pct"] = (d["Pred_USD_m2_Propio"] - d["USD_m2_Homogeneizado"]) / d["Pred_USD_m2_Propio"] * 100
    a = (d["Gap_Benchmark_pct"] >= umbral_gap) & (d["USD_m2_Homogeneizado"] <= d["P25_USD_m2_Comparable"])
    b = d["Gap_Hedonico_pct"] >= umbral_gap
    d["Categoria_Doble"] = np.select(
        [a & b, a & ~b, ~a & b], ["Confirmada_por_ambos", "Solo_benchmark", "Solo_hedonico"], "No_barata")
    d.loc[d["Estado_Propiedad"].eq("Necesita_obra") | d["Pred_USD_m2_Propio"].isna(), "Categoria_Doble"] = pd.NA
    return d
