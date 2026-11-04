"""
Modelo explicativo del precio por m² (regresión hedónica) y su validación.

- preparar_base_modelo: selecciona avisos y construye las variables del modelo.
- ajustar_hedonico: regresión de log(USD/m² homogeneizado) con errores robustos.
- tabla_efectos: efecto porcentual de cada variable, con intervalo de confianza.
- validar_fuera_de_muestra: holdout repetido contra el benchmark jerárquico.

El coeficiente de una variable indica la diferencia porcentual del USD/m²
asociada a esa característica, controlando por las demás. Es una asociación,
no una relación causal.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

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
