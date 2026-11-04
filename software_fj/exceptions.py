"""Módulo de excepciones personalizadas de Software FJ.

Define la jerarquía de excepciones de negocio para garantizar el manejo
robusto y estructurado de errores dentro del sistema sin interrumpir
la ejecución de la aplicación.

Autor: Marco Steven Rodríguez Montoya
Curso: Programación (213023) - UNAD
"""

from datetime import datetime
from typing import Optional, Any, Dict


class SoftwareFJException(Exception):
    """Clase base para todas las excepciones del dominio de Software FJ.

    Hereda de Exception y permite almacenar metadatos adicionales sobre
    el error, tales como un código de error, marca temporal y un diccionario
    con detalles de contexto para enriquecer los registros de log.
    """

    def __init__(
        self,
        mensaje: str,
        codigo_error: str = "ERR_GENERAL",
        detalles: Optional[Dict[str, Any]] = None
    ) -> None:
        """Inicializa la excepción base con metadatos contextuales.

        Args:
            mensaje: Descripción clara y humana del error ocurrido.
            codigo_error: Identificador alfanumérico único del tipo de error.
            detalles: Diccionario opcional con variables o parámetros del fallo.
        """
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo_error = codigo_error
        self.detalles = detalles or {}
        self.timestamp = datetime.now()

    def __str__(self) -> str:
        """Representación textual estándar de la excepción con su código."""
        return f"[{self.codigo_error}] {self.mensaje}"

    def formatear_para_log(self) -> str:
        """Formatea la información de la excepción para trazabilidad técnica."""
        info = f"{self.__class__.__name__} | Código: {self.codigo_error} | Mensaje: {self.mensaje}"
        if self.detalles:
            info += f" | Detalles: {self.detalles}"
        return info


class ClienteInvalidoException(SoftwareFJException):
    """Se lanza cuando los datos suministrados para un cliente son inválidos.

    Casos típicos:
    - Campos obligatorios vacíos o nulos (nombre, identificación, etc.).
    - Formato de correo electrónico no cumple con estándar RFC/regex.
    - Teléfono no cumple con el formato numérico esperado.
    """

    def __init__(
        self,
        mensaje: str,
        codigo_error: str = "ERR_CLIENTE_INVALIDO",
        detalles: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(mensaje, codigo_error, detalles)


class ServicioNoDisponibleException(SoftwareFJException):
    """Se lanza cuando un servicio solicitado no está habilitado o no tiene stock.

    Casos típicos:
    - Intento de alquilar un equipo físico cuyo inventario disponible es cero.
    - Servicio temporalmente fuera de línea o deshabilitado en el sistema.
    """

    def __init__(
        self,
        mensaje: str,
        codigo_error: str = "ERR_SERVICIO_NO_DISPONIBLE",
        detalles: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(mensaje, codigo_error, detalles)


class ReservaInvalidaException(SoftwareFJException):
    """Se lanza cuando los parámetros para agendar una reserva son inconsistentes.

    Casos típicos:
    - Duración en horas es menor o igual a cero.
    - Fecha de inicio con formato inválido o en el pasado sin justificación.
    - Asignación de servicios o clientes nulos o incompatibles.
    """

    def __init__(
        self,
        mensaje: str,
        codigo_error: str = "ERR_RESERVA_INVALIDA",
        detalles: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(mensaje, codigo_error, detalles)


class OperacionNoPermitidaException(SoftwareFJException):
    """Se lanza cuando se intenta realizar una transición de estado ilegal.

    Casos típicos:
    - Intentar cancelar una reserva que ya se encuentra en estado CANCELADA.
    - Intentar confirmar una reserva cancelada.
    - Eliminar o modificar entidades bloqueadas por el negocio.
    """

    def __init__(
        self,
        mensaje: str,
        codigo_error: str = "ERR_OPERACION_NO_PERMITIDA",
        detalles: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(mensaje, codigo_error, detalles)
