"""Módulo de configuración del subsistema de Logging para Software FJ.

Configura de manera centralizada la captura de eventos, advertencias y
excepciones tanto en consola como en un archivo persistente en disco (software_fj.log),
garantizando la trazabilidad exigida por la actividad académica.

Autor: Marco Steven Rodríguez Montoya
Curso: Programación (213023) - UNAD
"""

import logging
import sys
from pathlib import Path
from typing import Optional


# Ruta predeterminada para el archivo de logs en la raíz de la solución
LOG_FILE_PATH = Path(__file__).resolve().parent.parent / "software_fj.log"

# Formato estándar y detallado para cada entrada del registro
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | [%(name)s] | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configurar_logger_principal(
    archivo_log: Optional[Path] = None,
    nivel_consola: int = logging.INFO,
    nivel_archivo: int = logging.DEBUG
) -> logging.Logger:
    """Configura y retorna el logger raíz de la aplicación Software FJ.

    Crea un handler para la consola (StreamHandler) y un handler para el
    archivo físico (FileHandler) en disco, evitando la duplicación de handlers.

    Args:
        archivo_log: Ruta personalizada del archivo .log; por defecto usa software_fj.log.
        nivel_consola: Nivel mínimo de eventos visibles por consola.
        nivel_archivo: Nivel mínimo de eventos persistidos en disco.

    Returns:
        Instancia de logging.Logger configurada.
    """
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.DEBUG)

    # Evitar acumular handlers si la función se invoca múltiples veces
    if logger.handlers:
        return logger

    formateador = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    # 1. Handler para salida por Consola
    consola_handler = logging.StreamHandler(sys.stdout)
    consola_handler.setLevel(nivel_consola)
    consola_handler.setFormatter(formateador)
    logger.addHandler(consola_handler)

    # 2. Handler para archivo persistente en disco con codificación UTF-8
    destino_log = archivo_log or LOG_FILE_PATH
    try:
        # Asegurar que el directorio contenedor exista
        destino_log.parent.mkdir(parents=True, exist_ok=True)
        archivo_handler = logging.FileHandler(destino_log, mode="a", encoding="utf-8")
        archivo_handler.setLevel(nivel_archivo)
        archivo_handler.setFormatter(formateador)
        logger.addHandler(archivo_handler)
    except (OSError, IOError) as error_fs:
        # En caso de fallo con el sistema de archivos, avisar por consola sin abortar
        logger.warning(
            "No fue posible inicializar el FileHandler en '%s': %s",
            destino_log,
            error_fs
        )

    return logger


def obtener_logger(nombre_modulo: str) -> logging.Logger:
    """Retorna un sub-logger con el espacio de nombres de la jerarquía SoftwareFJ.

    Args:
        nombre_modulo: Nombre del módulo o clase solicitante.

    Returns:
        logging.Logger: Instancia conectada al logger raíz de la aplicación.
    """
    # Garantizar que el logger raíz esté inicializado
    configurar_logger_principal()
    return logging.getLogger(f"SoftwareFJ.{nombre_modulo}")
