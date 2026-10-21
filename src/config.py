"""
Parámetros centralizados del proyecto.

Todos los umbrales, rutas y supuestos que afectan los resultados se definen
acá y solo acá. Los módulos de `src/` y los notebooks los importan; ningún
notebook debe volver a escribir estos valores a mano. Si se cambia un
parámetro, se cambia en este archivo y se vuelven a correr los notebooks.
"""

from pathlib import Path


# RUTAS (relativas a la raíz del repositorio)

RAIZ = Path(__file__).resolve().parent.parent

DATA_DIR = RAIZ / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EXTERNAL_DIR = DATA_DIR / "external"
REPORTS_DIR = RAIZ / "reports"

RAW_PATH = RAW_DIR / "remax_caba_propiedades.csv"
BASE_LIMPIA = PROCESSED_DIR / "remax_deptos_limpio.csv"
BASE_FEATURES = PROCESSED_DIR / "remax_deptos_features.csv"
SUPUESTOS_FLIPPING = DATA_DIR / "supuestos_flipping.csv"


# BASE RAW (copia en Google Drive por su tamaño, ~36 MB)

RAW_DRIVE_ID = "1EapNHaHFCOYzIgedcWNqcLYoFHDkF3QE"

# Huella SHA-256 de la extracción de referencia (corte 26/09/2026).
# Se completa una sola vez corriendo `src.datos.calcular_sha256(RAW_PATH)`
# sobre la base descargada. Mientras sea None, la verificación solo informa
# el hash calculado y no bloquea la ejecución.
RAW_SHA256 = None


# BENCHMARK Y CLASIFICACIÓN DE OPORTUNIDADES

# Mínimo de comparables por grupo en el benchmark jerárquico (y en el PER)
MIN_COMPARABLES = 10

# Umbral de gap de subvaluación (%) para considerar "barata" una propiedad.
# Recalibrado de 15 % a 25 % a partir del análisis de sensibilidad
# (notebook 03, sección 7.3). Es el valor usado en la corrida reportada.
UMBRAL_GAP = 25

# Umbrales evaluados en el análisis de sensibilidad
UMBRALES_SENSIBILIDAD = [10, 15, 20, 25]


# ESCENARIOS DEL PRECIO ESPERADO RECICLADO (PER)

# Cuantil de los comparables usado como valor post-obra en cada escenario
ESCENARIOS_PER = {
    "Conservador": "PER_USD_m2_P25",
    "Base": "PER_USD_m2_Base",
    "Optimista": "PER_USD_m2_P75",
}
ESCENARIOS = list(ESCENARIOS_PER)


# COSTOS DE LA OPERACIÓN

# Costos de transacción totales (compra + venta, % del precio) usados en la
# PreEntrega 2 como primera vara del potencial bruto. El desglose por
# componente y escenario está en data/supuestos_flipping.csv.
COSTOS_TRANSACCION_PCT = 12
