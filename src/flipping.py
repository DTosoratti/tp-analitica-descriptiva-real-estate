"""
Modelo económico de flipping: costos, rentabilidad y regla de decisión.

Toda la lógica estable del modelo vive acá; la notebook 07 solo la ejecuta,
muestra resultados e interpreta. Los supuestos de costo se leen de
`data/supuestos_flipping.csv` (con su fuente) y los umbrales de decisión de
`src/config.py`. Ningún valor se escribe a mano en la notebook.

Fórmulas por escenario e (conservador, base, optimista):

    compra      = precio_compra × (1 + costos_compra)
    obra        = sup_cubierta × costo_m2[nivel] × factor_premium × (1 + contingencia)
    meses       = plazo_obra[nivel] + plazo_comercializacion
    tenencia    = expensas_usd_mes × meses
    capital     = compra + obra + tenencia
    oportunidad = capital × tasa_anual × meses / 12
    inversion   = capital + oportunidad
    venta_neta  = PER_e × (1 − costos_venta)
    ROI         = (venta_neta − inversion) / inversion

Para cada escenario, el precio máximo de oferta despeja el precio de compra
que deja un ROI igual al margen mínimo:

    P_max_e(m) = (venta_neta / ((1 + k) (1 + m)) − obra − tenencia) / (1 + costos_compra),
    con k = tasa_anual × meses / 12.

El precio máximo de oferta que usa la regla de decisión (`Precio_Max_Oferta_USD`)
es el menor de tres techos, de modo que al precio ofertado se cumplen todas las
condiciones económicas de la regla del README:

    1. ROI base ≥ margen mínimo          → P_max_Base(margen)
    2. ROI conservador ≥ 0               → P_max_Conservador(0)
    3. gap de subvaluación ≥ UMBRAL_GAP  → Precio_Esperado × (1 − UMBRAL_GAP / 100)
"""

import re

import numpy as np
import pandas as pd

from src.config import (
    CUANTIL_BARRIO_PREMIUM,
    DESCUENTO_NEGOCIABLE_PCT,
    MARGEN_MINIMO_PCT,
    MIN_COMPARABLES,
    PRESUPUESTO_MAX_USD,
    SUPUESTOS_FLIPPING,
    TIPO_CAMBIO_ARS_USD,
    UMBRAL_GAP,
)
from src.patrones import PATRONES

ESCENARIOS = ["Conservador", "Base", "Optimista"]
COL_CSV = {"Conservador": "conservador", "Base": "base", "Optimista": "optimista"}
COL_PER = {"Conservador": "PER_Conservador", "Base": "PER_Base", "Optimista": "PER_Optimista"}

# Componentes del CSV que están expresados en porcentaje
PCT = {"contingencia", "costos_compra", "costos_venta", "tasa_oportunidad"}


def cargar_supuestos(ruta=SUPUESTOS_FLIPPING):
    """
    Lee los supuestos de costo y devuelve {escenario: {componente: valor}}.

    Los porcentajes se devuelven como fracción (7 → 0.07). Las filas no
    numéricas (costo de tenencia = "Expensas") se omiten: la tenencia se
    calcula con las expensas de cada aviso.
    """
    tabla = pd.read_csv(ruta).set_index("componente")
    supuestos = {}
    for esc in ESCENARIOS:
        valores = pd.to_numeric(tabla[COL_CSV[esc]], errors="coerce").dropna()
        supuestos[esc] = {
            comp: (v / 100 if comp in PCT else float(v)) for comp, v in valores.items()
        }
    return supuestos


def asignar_nivel_obra(df):
    """
    Nivel de obra según la evidencia del aviso (README, "Origen del costo"):

    - "Integral": señal fuerte ("a reciclar", "a refaccionar"; columna A_Refaccionar).
    - "Media":    solo señal débil ("a actualizar", "a modernizar", ...).
    - "Integral": sin evidencia clara, como caso conservador.
    """
    texto = (df["Titulo"].fillna("") + " " + df["Descripcion"].fillna("")).str.lower()
    debil = texto.str.contains(PATRONES["necesita_obra_debil"], regex=True, na=False)
    fuerte = df["A_Refaccionar"].fillna(False).astype(bool)
    nivel = np.where(fuerte, "Integral", np.where(debil, "Media", "Integral"))
    evidencia = np.where(fuerte, "Señal fuerte", np.where(debil, "Señal débil", "Sin evidencia"))
    return pd.Series(nivel, index=df.index), pd.Series(evidencia, index=df.index)


def barrios_premium(df_mercado, cuantil=CUANTIL_BARRIO_PREMIUM):
    """Barrios cuyo USD/m² homogeneizado mediano está en el cuartil superior."""
    mediana = df_mercado.groupby("Barrio_Oficial")["USD_m2_Homogeneizado"].median()
    return set(mediana[mediana >= mediana.quantile(cuantil)].index)


def calcular_escenarios(df, supuestos, premium, descuento_compra=0.0,
                        tipo_cambio=TIPO_CAMBIO_ARS_USD):
    """
    Agrega costos, inversión, ganancia y ROI de cada escenario.

    `descuento_compra` (fracción) reduce el precio de compra respecto del
    publicado, para el análisis de sensibilidad a la negociación.
    """
    out = df.copy()
    nivel = out["Nivel_Obra"].str.lower()
    out["Barrio_Premium"] = out["Barrio_Oficial"].isin(premium)
    out["Expensas_USD_Mensuales"] = out["Expensas_Imputadas"] / tipo_cambio
    precio = out["Precio_Valor"] * (1 - descuento_compra)
    out["Precio_Compra_USD"] = precio

    for esc in ESCENARIOS:
        s = supuestos[esc]
        costo_m2 = nivel.map(lambda n: s[f"costo_obra_{n}"])
        plazo_obra = nivel.map(lambda n: s[f"plazo_obra_{n}"])
        factor = np.where(out["Barrio_Premium"], s["factor_terminacion_premium"], 1.0)
        meses = plazo_obra + s["plazo_comercializacion"]

        compra = precio * (1 + s["costos_compra"])
        obra = out["Superficie_Cubierta_m2"] * costo_m2 * factor * (1 + s["contingencia"])
        tenencia = out["Expensas_USD_Mensuales"] * meses
        capital = compra + obra + tenencia
        oportunidad = capital * s["tasa_oportunidad"] * meses / 12
        inversion = capital + oportunidad
        venta_neta = out[COL_PER[esc]] * (1 - s["costos_venta"])
        ganancia = venta_neta - inversion

        out[f"Meses_Operacion_{esc}"] = meses
        out[f"Costo_Obra_{esc}_USD"] = obra
        out[f"Costo_Tenencia_{esc}_USD"] = tenencia
        out[f"Costo_Oportunidad_{esc}_USD"] = oportunidad
        out[f"Inversion_Total_{esc}_USD"] = inversion
        out[f"Ganancia_Neta_{esc}_USD"] = ganancia
        out[f"ROI_{esc}_pct"] = ganancia / inversion * 100

        k = s["tasa_oportunidad"] * meses / 12

        def pmax(margen_pct):
            return (venta_neta / ((1 + k) * (1 + margen_pct / 100))
                    - obra - tenencia) / (1 + s["costos_compra"])

        out[f"Precio_Max_Oferta_{esc}_USD"] = pmax(MARGEN_MINIMO_PCT)
        out[f"Descuento_Requerido_{esc}_pct"] = (
            1 - out[f"Precio_Max_Oferta_{esc}_USD"] / out["Precio_Valor"]) * 100
        if esc == "Conservador":
            out["Precio_Max_ROI_Conservador_0_USD"] = pmax(0)

    return out


TECHOS_OFERTA = {
    "ROI base ≥ margen": "Precio_Max_Oferta_Base_USD",
    "ROI conservador ≥ 0": "Precio_Max_ROI_Conservador_0_USD",
    "Gap ≥ umbral": "Precio_Max_Gap_USD",
}


def precio_max_oferta(df, umbral_gap=UMBRAL_GAP):
    """
    Precio máximo de oferta que cumple a la vez las tres condiciones económicas
    de la regla (ver docstring del módulo) y qué condición lo determina.

    Devuelve un DataFrame con `Precio_Max_Gap_USD`, `Precio_Max_Oferta_USD`,
    `Descuento_Requerido_pct` (sobre el precio publicado) y `Restriccion_Activa`.
    """
    out = pd.DataFrame(index=df.index)
    out["Precio_Max_Gap_USD"] = df["Precio_Esperado"] * (1 - umbral_gap / 100)
    techos = pd.concat([df.get(c, out.get(c)) for c in TECHOS_OFERTA.values()], axis=1)
    techos.columns = list(TECHOS_OFERTA)
    out["Precio_Max_Oferta_USD"] = techos.min(axis=1)
    out["Restriccion_Activa"] = techos.idxmin(axis=1)
    out["Descuento_Requerido_pct"] = (1 - out["Precio_Max_Oferta_USD"] / df["Precio_Valor"]) * 100
    return out


def verificar_oferta(df, supuestos, premium, umbral_gap=UMBRAL_GAP):
    """
    Recalcula el modelo completo al precio máximo de oferta de cada unidad y
    devuelve ROI conservador, ROI base, gap e inversión base a ese precio.
    Sirve para comprobar que la regla de oferta hace lo que declara.
    """
    desc = (df["Descuento_Requerido_pct"] / 100).to_numpy()
    filas = []
    for i, d in zip(df.index, desc):
        r = calcular_escenarios(df.loc[[i]], supuestos, premium, descuento_compra=d).iloc[0]
        filas.append({
            "ROI_Conservador_Oferta_pct": r["ROI_Conservador_pct"],
            "ROI_Base_Oferta_pct": r["ROI_Base_pct"],
            "Gap_Oferta_pct": (1 - r["Precio_Compra_USD"] / df.at[i, "Precio_Esperado"]) * 100,
            "Inversion_Base_Oferta_USD": r["Inversion_Total_Base_USD"],
        })
    return pd.DataFrame(filas, index=df.index)


def clasificar_robustez(df):
    """Categoría según en qué escenarios el ROI es positivo."""
    c, b, o = (df[f"ROI_{e}_pct"] > 0 for e in ESCENARIOS)
    return pd.Series(np.select(
        [c & b & o, ~c & b & o, ~b & o, ~o],
        ["Rentable en los tres escenarios", "Rentable en base y optimista",
         "Rentable solo en optimista", "No rentable"],
        default="Revisar"), index=df.index)


PATRON_NO_RESIDENCIAL = (
    r"\b(?:oficina|oficinas|consultorio|consultorios|apto profesional|"
    r"uso profesional|uso comercial|local comercial)\b"
)


def alertas(df):
    """Alertas de revisión: indican que el resultado puede no ser confiable."""
    texto = (df["Titulo"].fillna("") + " " + df["Descripcion"].fillna("")).str.lower()
    a = pd.DataFrame(index=df.index)
    a["Alerta_Uso_No_Residencial"] = texto.str.contains(PATRON_NO_RESIDENCIAL, regex=True)
    a["Alerta_Superficie_Alta"] = df["Superficie_Cubierta_m2"] > 200
    a["Alerta_ROI_Extremo"] = df["ROI_Base_pct"] > 80
    a["Alerta_PER_Nivel_4"] = df["PER_Nivel"] == 4
    a["Alerta_Senal_Contradictoria"] = df["Flag_Senal_Contradictoria"].fillna(False).astype(bool)
    a["Alerta_Expensas_Imputadas"] = df["Flag_Expensas_Imputadas"].fillna(False).astype(bool)
    return a


def aplicar_regla(df, margen=MARGEN_MINIMO_PCT, presupuesto=PRESUPUESTO_MAX_USD,
                  descuento_max=DESCUENTO_NEGOCIABLE_PCT, min_comp=MIN_COMPARABLES):
    """
    Regla de decisión del README. Las condiciones económicas (ROI base ≥ margen,
    ROI conservador ≥ 0 y gap ≥ umbral) se evalúan al precio máximo de oferta
    (`precio_max_oferta`), que las cumple todas por construcción:

    - "Comprar al precio publicado": el precio publicado ya cumple las tres
      condiciones (descuento requerido ≤ 0), comparables ≥ mínimo, inversión
      base ≤ presupuesto y sin alertas.
    - "Ofertar con descuento": igual, pero hace falta un descuento positivo
      y ≤ descuento_max para cumplirlas.
    - "Revisar manualmente": cerraría al precio publicado o con descuento,
      pero tiene alertas.
    - "Descartar": el resto.

    Requiere las columnas de `precio_max_oferta` y `verificar_oferta`
    (`Descuento_Requerido_pct`, `Inversion_Base_Oferta_USD`).
    """
    soporte = df["PER_N_Comparables"] >= min_comp
    presup = df["Inversion_Base_Oferta_USD"] <= presupuesto
    sin_alertas = df["Cantidad_Alertas"] == 0
    desc = df["Descuento_Requerido_pct"]
    cumple_precio = desc <= 0
    cumple_desc = (desc > 0) & (desc <= descuento_max)
    base = soporte & presup
    return pd.Series(np.select(
        [base & sin_alertas & cumple_precio,
         base & sin_alertas & cumple_desc,
         base & ~sin_alertas & (cumple_precio | cumple_desc)],
        ["Comprar al precio publicado", "Ofertar con descuento", "Revisar manualmente"],
        default="Descartar"), index=df.index)


def resumen_escenarios(df):
    """ROI mediano y cantidad de operaciones rentables por escenario."""
    filas = []
    for e in ESCENARIOS:
        roi = df[f"ROI_{e}_pct"]
        filas.append({"Escenario": e, "ROI_mediano_pct": roi.median(),
                      "Rentables": int((roi > 0).sum()),
                      "Rentables_pct": (roi > 0).mean() * 100,
                      f"Con_ROI_≥_{MARGEN_MINIMO_PCT}%": int((roi >= MARGEN_MINIMO_PCT).sum())})
    return pd.DataFrame(filas)
