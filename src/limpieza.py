"""
Funciones de auditoría y limpieza para la base RE/MAX CABA.

- Auditorías: resumen de calidad, categóricas, numéricas y reglas de consistencia.
- Registro de pasos: cada exclusión o modificación queda anotada para
  reconstruir el embudo de limpieza (raw -> base analítica).
- Excepciones manuales: las correcciones por ID viven en
  data/excepciones_manuales.csv, no hardcodeadas en el notebook.
"""

import re

import numpy as np
import pandas as pd


# AUDITORÍAS


def resumen_calidad(df):
    """Tipo, nulos y valores únicos por columna."""
    resumen = pd.DataFrame({
        "Tipo": df.dtypes.astype(str),
        "Nulos": df.isna().sum(),
        "Nulos_%": (df.isna().mean() * 100).round(2),
        "Unicos": df.nunique(dropna=True),
    })
    return resumen.sort_values("Nulos_%", ascending=False)


def auditar_categorica(df, columna):
    """Frecuencia absoluta y relativa de una variable categórica."""
    return (
        df[columna]
        .value_counts(dropna=False)
        .rename_axis(columna)
        .reset_index(name="Cantidad")
        .assign(Porcentaje=lambda x: (x["Cantidad"] / len(df) * 100).round(2))
    )


def auditar_numericas(df, columnas):
    """Nulos, ceros, negativos y distribución de varias numéricas en una tabla."""
    filas = []
    for col in columnas:
        s = df[col]
        filas.append({
            "Variable": col,
            "Nulos": s.isna().sum(),
            "Ceros": (s == 0).sum(),
            "Negativos": (s < 0).sum(),
            "Min": s.min(),
            "P01": s.quantile(0.01),
            "P25": s.quantile(0.25),
            "Mediana": s.median(),
            "P75": s.quantile(0.75),
            "P99": s.quantile(0.99),
            "Max": s.max(),
        })
    return pd.DataFrame(filas).set_index("Variable").round(2)


# Reglas de consistencia: cada regla devuelve una máscara con los casos
# que la VIOLAN. Se agregan acá en vez de escribir un chequeo por celda.
REGLAS_CONSISTENCIA = {
    "Cubierta > Total": lambda d: d["Superficie_Cubierta_m2"] > d["Superficie_Total_m2"],
    "Superficie total <= 0": lambda d: d["Superficie_Total_m2"] <= 0,
    "Precio <= 0": lambda d: d["Precio_Valor"] <= 0,
    "Ambientes = 0": lambda d: d["Ambientes"] == 0,
    "Dormitorios >= Ambientes": lambda d: d["Dormitorios"] >= d["Ambientes"],
    "Antigüedad negativa": lambda d: d["Antiguedad"] < 0,
    "USD/m² informado != calculado (>1%)": lambda d: (
        (d["Precio_m2_Total"] - d["Precio_Valor"] / d["Superficie_Total_m2"]).abs()
        > 0.01 * d["Precio_m2_Total"]
    ),
}


def auditar_reglas(df, reglas=REGLAS_CONSISTENCIA):
    """Cantidad de registros que violan cada regla de consistencia."""
    filas = []
    for nombre, regla in reglas.items():
        mask = regla(df).fillna(False)
        filas.append({"Regla": nombre, "Casos": int(mask.sum())})
    return pd.DataFrame(filas).set_index("Regla")


def casos_regla(df, nombre, columnas=None, reglas=REGLAS_CONSISTENCIA):
    """Devuelve los registros que violan una regla, para inspección."""
    mask = reglas[nombre](df).fillna(False)
    return df.loc[mask, columnas] if columnas else df.loc[mask]


# TEXTO Y PATRONES


def texto_propiedad(df):
    """Título + descripción en un solo texto (para buscar patrones)."""
    return df["Titulo"].fillna("") + " " + df["Descripcion"].fillna("")


def buscar_patron(df, patron, donde="texto"):
    """
    Máscara booleana de registros que contienen el patrón.
    donde: "titulo", "descripcion" o "texto" (ambos).
    """
    fuentes = {
        "titulo": df["Titulo"],
        "descripcion": df["Descripcion"],
        "texto": texto_propiedad(df),
    }
    return fuentes[donde].str.contains(patron, case=False, na=False, regex=True)


# REGISTRO DE PASOS


def excluir(df, mask, paso, criterio, registro):
    """Excluye los registros de la máscara y anota el paso."""
    mask = mask.reindex(df.index).fillna(False).astype(bool)
    n_antes = len(df)
    df_nuevo = df.loc[~mask].copy()
    registro.append({
        "Paso": paso,
        "Tipo": "Exclusión",
        "Criterio": criterio,
        "Registros_afectados": int(mask.sum()),
        "Filas_antes": n_antes,
        "Filas_despues": len(df_nuevo),
    })
    return df_nuevo


def modificar(df, mask, columna, valor, paso, criterio, registro):
    """Reemplaza el valor de una columna en la máscara y anota el paso."""
    mask = mask.reindex(df.index).fillna(False).astype(bool)
    df = df.copy()
    df.loc[mask, columna] = valor
    registro.append({
        "Paso": paso,
        "Tipo": f"Modificación ({columna})",
        "Criterio": criterio,
        "Registros_afectados": int(mask.sum()),
        "Filas_antes": len(df),
        "Filas_despues": len(df),
    })
    return df


def tabla_registro(registro):
    """Embudo de limpieza en formato tabla."""
    return pd.DataFrame(registro)


# EXCEPCIONES MANUALES


def cargar_excepciones(path="data/excepciones_manuales.csv"):
    return pd.read_csv(path, dtype={"valor_nuevo": str})


def _convertir_valor(valor, serie):
    """Convierte el valor de la tabla (texto) al tipo de la columna."""
    if pd.isna(valor) or valor == "NaN":
        return np.nan
    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(valor)
    return valor


def aplicar_excepciones(df, excepciones, registro, etapa):
    """
    Aplica las excepciones de una etapa ("limpieza" o "estado").

    Acciones:
      - excluir: elimina el registro
      - reemplazar: asigna valor_nuevo en columna (valor_nuevo = NaN deja faltante)

    Devuelve (df, reporte). El reporte indica si cada ID se encontró en la
    base: si la corrida del scraper cambió, un ID viejo puede no existir.
    """
    exc = excepciones.loc[excepciones["etapa"] == etapa].copy()
    exc["encontrado"] = exc["ID"].isin(df["ID"])

    # Exclusiones
    ids_excluir = exc.loc[(exc["accion"] == "excluir") & exc["encontrado"], "ID"]
    if len(ids_excluir):
        df = excluir(
            df, df["ID"].isin(ids_excluir), f"Excepciones manuales ({etapa})",
            "Exclusiones documentadas en excepciones_manuales.csv", registro,
        )

    # Reemplazos
    df = df.copy()
    reemplazos = exc.loc[(exc["accion"] == "reemplazar") & exc["encontrado"]]
    for _, fila in reemplazos.iterrows():
        mask = df["ID"] == fila["ID"]
        df.loc[mask, fila["columna"]] = _convertir_valor(
            fila["valor_nuevo"], df[fila["columna"]]
        )
    if len(reemplazos):
        registro.append({
            "Paso": f"Excepciones manuales ({etapa})",
            "Tipo": "Modificación (varias columnas)",
            "Criterio": "Reemplazos documentados en excepciones_manuales.csv",
            "Registros_afectados": int(reemplazos["ID"].nunique()),
            "Filas_antes": len(df),
            "Filas_despues": len(df),
        })

    reporte = exc[["ID", "accion", "columna", "valor_nuevo", "motivo", "encontrado"]]
    return df, reporte


# TEXTO: NORMALIZACIÓN, NEGACIÓN Y AMENITIES


def normalizar_texto(serie):
    """Minúsculas, sin acentos y sin espacios repetidos (incluye saltos de línea)."""
    return (
        serie.fillna("").astype(str).str.lower()
        .str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")
        .str.split().str.join(" ")
    )


def contiene_sin_negacion(serie, patron, negacion):
    """
    True si el texto contiene el patrón en al menos una aparición que NO esté
    precedida por una negación ("no requiere refacción" no cuenta como match).
    `serie` debe estar normalizada (minúsculas, sin acentos).
    """
    rx = re.compile(patron)
    rx_neg = re.compile(negacion)

    def evaluar(texto):
        for m in rx.finditer(texto):
            previo = texto[max(0, m.start() - 40):m.start()]
            if not rx_neg.search(previo):
                return True
        return False

    return serie.apply(evaluar)


def marcar_amenities(df, amenities, col_lista="Amenities", col_texto="Texto_Normalizado"):
    """
    Una columna booleana por amenity: True si figura en la lista estructurada
    de la fuente o si se menciona en el texto del aviso.
    Devuelve un DataFrame con columnas Nombre, Nombre_Lista y Nombre_Texto.
    """
    lista = df[col_lista].fillna("").astype(str)
    salida = pd.DataFrame(index=df.index)
    for nombre, regla in amenities.items():
        patron_lista = "|".join(re.escape(v) for v in regla["lista"])
        en_lista = lista.str.contains(patron_lista, case=False, regex=True)
        en_texto = df[col_texto].str.contains(regla["texto"], regex=True)
        salida[f"{nombre}_Lista"] = en_lista
        salida[f"{nombre}_Texto"] = en_texto
        salida[nombre] = en_lista | en_texto
    return salida
