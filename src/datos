"""
Acceso a la base raw y control de versión por hash.
 
La base raw completa (~36 MB) no se versiona en GitHub. Se conserva una copia
en Google Drive y se identifica por su huella SHA-256 (`RAW_SHA256` en
src/config.py). Así, cualquier ejecución puede comprobar que trabaja sobre la
misma extracción que se reportó en el informe.
 
Uso desde un notebook:
 
    from src.datos import obtener_raw
    RAW_PATH = obtener_raw()
"""
 
import hashlib
from pathlib import Path
 
from src.config import RAW_PATH, RAW_DRIVE_ID, RAW_SHA256
 
 
def calcular_sha256(ruta, tam_bloque=1 << 20):
    """Huella SHA-256 de un archivo, leída por bloques."""
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(tam_bloque), b""):
            h.update(bloque)
    return h.hexdigest()
 
 
def descargar_raw(ruta=RAW_PATH, drive_id=RAW_DRIVE_ID):
    """Descarga la base raw desde Google Drive (solo si no existe localmente)."""
    ruta = Path(ruta)
    if ruta.exists():
        return ruta
    try:
        import gdown
    except ImportError as e:
        raise ImportError(
            "Falta la base raw y no está instalado gdown. Instalarlo "
            "(pip install gdown) o copiar manualmente el CSV en "
            f"{ruta}."
        ) from e
    ruta.parent.mkdir(parents=True, exist_ok=True)
    gdown.download(id=drive_id, output=str(ruta), quiet=False)
    return ruta
 
 
def verificar_raw(ruta=RAW_PATH, sha256_esperado=RAW_SHA256):
    """
    Compara el hash del archivo con el de la extracción de referencia.
 
    - Si coincide, lo informa.
    - Si no coincide, lanza un error: el análisis no correría sobre la misma base.
    - Si todavía no hay hash de referencia, informa el calculado para
      registrarlo en src/config.py.
    """
    actual = calcular_sha256(ruta)
    if sha256_esperado is None:
        print("SHA-256 de la base raw:", actual)
        print("Todavía no hay hash de referencia: copiar este valor en "
              "RAW_SHA256 (src/config.py).")
    elif actual != sha256_esperado:
        raise ValueError(
            "La base raw no coincide con la extracción de referencia.\n"
            f"  esperado: {sha256_esperado}\n  obtenido: {actual}"
        )
    else:
        print("Base raw verificada (SHA-256 coincide con la referencia).")
    return actual
 
 
def obtener_raw(ruta=RAW_PATH):
    """Descarga la base raw si falta, verifica su hash y devuelve la ruta."""
    ruta = descargar_raw(ruta)
    verificar_raw(ruta)
    return Path(ruta)
 
