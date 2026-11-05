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

El precio máximo de oferta despeja el precio de compra que deja un ROI igual
al margen mínimo:

    P_max = (venta_neta / ((1 + k) (1 + margen)) − obra − tenencia) / (1 + costos_compra),
    con k = tasa_anual × meses / 12.
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
        pmax = (venta_neta / ((1 + k) * (1 + MARGEN_MINIMO_PCT / 100))
                - obra - tenencia) / (1 + s["costos_compra"])
        out[f"Precio_Max_Oferta_{esc}_USD"] = pmax
        out[f"Descuento_Requerido_{esc}_pct"] = (1 - pmax / out["Precio_Valor"]) * 100

    return out


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
    Regla de decisión del README, con una categoría intermedia para el caso
    en que la operación solo cierra si se negocia el precio:

    - "Comprar al precio publicado": ROI base ≥ margen, ROI conservador ≥ 0,
      inversión base ≤ presupuesto, comparables ≥ mínimo y sin alertas.
    - "Ofertar con descuento": cumple soporte, presupuesto y alertas, y el
      descuento necesario para alcanzar el margen en el escenario base es
      ≤ descuento_max.
    - "Revisar manualmente": cerraría con descuento, pero tiene alertas.
    - "Descartar": el resto.
    """
    soporte = df["PER_N_Comparables"] >= min_comp
    presup = df["Inversion_Total_Base_USD"] <= presupuesto
    sin_alertas = df["Cantidad_Alertas"] == 0
    cumple_precio = (df["ROI_Base_pct"] >= margen) & (df["ROI_Conservador_pct"] >= 0)
    cumple_desc = df["Descuento_Requerido_Base_pct"] <= descuento_max
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
