"""
Benchmark jerárquico de propiedades comparables.

La misma lógica se usa para dos KPIs:
- Benchmark USD/m² (mediana de comparables habilitados, con leave-one-out).
- Precio Esperado Reciclado (PER): cuantiles de comparables en buen estado o
  reciclados, calculados para las propiedades que necesitan obra.

Para cada propiedad se busca el primer nivel de la jerarquía cuyo grupo tenga
al menos `min_n` comparables y se calculan los cuantiles del valor en ese grupo.
"""

import numpy as np
import pandas as pd


# Jerarquía de grupos de comparables (de más fino a más amplio)
NIVELES_COMPARABLES = {
    1: ["Barrio_Oficial", "Ambientes_Grupo", "Banda_Superficie", "Banda_Antiguedad"],
    2: ["Barrio_Oficial", "Ambientes_Grupo", "Banda_Superficie"],
    3: ["Comuna", "Ambientes_Grupo", "Banda_Superficie"],
    4: ["Comuna", "Ambientes_Grupo"],
}


def benchmark_jerarquico(df, valor, niveles, mask_referencia, mask_objetivo=None,
                         min_n=10, leave_one_out=True, cuantiles=(0.25, 0.50, 0.75)):
    """
    Cuantiles de `valor` entre comparables, con ampliación jerárquica.

    Parámetros
    ----------
    df : DataFrame con las columnas de agrupamiento y `valor`.
    valor : columna sobre la que se calculan los cuantiles (p. ej. USD/m²).
    niveles : dict {nivel: [columnas del grupo]}, del más fino al más amplio.
    mask_referencia : máscara de las filas que pueden actuar como comparables.
    mask_objetivo : máscara de las filas a las que se les calcula el benchmark
        (por defecto, todas).
    min_n : mínimo de comparables por grupo.
    leave_one_out : si True, una fila que también es comparable se excluye de
        su propio grupo (el mínimo se cuenta sin ella).
    cuantiles : cuantiles a calcular.

    Devuelve
    --------
    DataFrame con el mismo índice que `df` y columnas Q25, Q50, Q75 (según
    `cuantiles`), N (comparables usados) y Nivel (nivel de la jerarquía).
    Las filas sin ningún nivel con `min_n` comparables quedan en NaN.

    Las columnas de agrupamiento no deben tener valores faltantes.
    """
    referencia = mask_referencia.reindex(df.index).fillna(False).astype(bool)
    if mask_objetivo is None:
        pendientes = pd.Series(True, index=df.index)
    else:
        pendientes = mask_objetivo.reindex(df.index).fillna(False).astype(bool).copy()

    nombres = [f"Q{int(round(q * 100))}" for q in cuantiles]
    resultados = []

    for nivel, columnas in niveles.items():
        if not pendientes.any():
            break

        # Valores de los comparables por grupo
        valores_grupo = {
            clave: serie.dropna()
            for clave, serie in df.loc[referencia].groupby(columnas, observed=True)[valor]
        }

        asignadas = []
        grupos_pendientes = df.loc[pendientes].groupby(columnas, observed=True).groups
        for clave, filas in grupos_pendientes.items():
            if clave not in valores_grupo:
                continue
            serie = valores_grupo[clave]
            valores = serie.to_numpy()
            posicion = {etiqueta: i for i, etiqueta in enumerate(serie.index)}

            for idx in filas:
                if leave_one_out and idx in posicion:
                    vals = np.delete(valores, posicion[idx])
                else:
                    vals = valores
                if vals.size < min_n:
                    continue
                resultados.append((idx, *np.quantile(vals, cuantiles), vals.size, nivel))
                asignadas.append(idx)

        pendientes.loc[asignadas] = False

    salida = pd.DataFrame(np.nan, index=df.index, columns=nombres + ["N"])
    salida["Nivel"] = pd.Series(pd.NA, index=df.index, dtype="Int64")
    if resultados:
        tabla = pd.DataFrame(resultados, columns=["idx"] + nombres + ["N", "Nivel"]).set_index("idx")
        salida.loc[tabla.index, nombres + ["N"]] = tabla[nombres + ["N"]].values
        salida.loc[tabla.index, "Nivel"] = tabla["Nivel"].astype("Int64")
    return salida
