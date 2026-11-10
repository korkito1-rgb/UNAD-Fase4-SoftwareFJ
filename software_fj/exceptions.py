"""Módulo de excepciones personalizadas para Software FJ.
Estudiante: Marco Steven Rodríguez Montoya
Curso: Programación (213023) - Fase 4
UNAD - 2026
"""

from datetime import datetime


class SoftwareFJException(Exception):
    """Clase base para las excepciones del sistema Software FJ."""
    def __init__(self, mensaje: str, codigo: str = "ERR-GENERAL"):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo
        self.fecha_hora = datetime.now()

    def __str__(self):
        return f"[{self.codigo}] {self.mensaje}"


class ClienteInvalidoException(SoftwareFJException):
    """Se lanza cuando los datos de un cliente no pasan las validaciones."""
    def __init__(self, mensaje: str, codigo: str = "ERR-CLI"):
        super().__init__(mensaje, codigo)


class ServicioNoDisponibleException(SoftwareFJException):
    """Se lanza cuando un servicio no está disponible o no hay unidades en inventario."""
    def __init__(self, mensaje: str, codigo: str = "ERR-SRV-STOCK"):
        super().__init__(mensaje, codigo)


class ReservaInvalidaException(SoftwareFJException):
    """Se lanza cuando los parámetros de una reserva son inconsistentes (duración <= 0, etc.)."""
    def __init__(self, mensaje: str, codigo: str = "ERR-RES-INVALIDA"):
        super().__init__(mensaje, codigo)


class OperacionNoPermitidaException(SoftwareFJException):
    """Se lanza cuando se intenta realizar una acción inválida sobre una reserva."""
    def __init__(self, mensaje: str, codigo: str = "ERR-OP-NO-PERMITIDA"):
        super().__init__(mensaje, codigo)
