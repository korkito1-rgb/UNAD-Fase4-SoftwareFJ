"""Configuración del sistema de logging para Software FJ.
Guarda los eventos en consola y en el archivo software_fj.log.
"""

import logging
import sys
from pathlib import Path

# Definimos la ruta del archivo de log en la carpeta principal
RUTA_LOG = Path(__file__).resolve().parent.parent / "software_fj.log"

# Formato sencillo con fecha, nivel de error, módulo y mensaje
FORMATO = "%(asctime)s | %(levelname)-7s | [%(name)s] | %(message)s"
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"


def configurar_logger():
    """Configura el logger general con salida a consola y al archivo de log."""
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.DEBUG)

    # Si ya tiene handlers configurados, no los agregamos de nuevo
    if logger.handlers:
        return logger

    formateador = logging.Formatter(fmt=FORMATO, datefmt=FORMATO_FECHA)

    # Salida por consola
    handler_consola = logging.StreamHandler(sys.stdout)
    handler_consola.setLevel(logging.INFO)
    handler_consola.setFormatter(formateador)
    logger.addHandler(handler_consola)

    # Salida a archivo software_fj.log en UTF-8
    try:
        handler_archivo = logging.FileHandler(RUTA_LOG, mode="a", encoding="utf-8")
        handler_archivo.setLevel(logging.DEBUG)
        handler_archivo.setFormatter(formateador)
        logger.addHandler(handler_archivo)
    except Exception as e:
        print(f"Advertencia: No se pudo crear el archivo de log: {e}")

    return logger


def obtener_logger(nombre_modulo: str):
    """Devuelve un logger para el módulo indicado."""
    configurar_logger()
    return logging.getLogger(f"SoftwareFJ.{nombre_modulo}")
