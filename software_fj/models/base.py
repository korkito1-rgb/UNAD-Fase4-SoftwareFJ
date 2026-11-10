"""Clase base abstracta para las entidades del modelo.
Define el identificador que toda clase del sistema debe tener.
"""

from abc import ABC, abstractmethod
from datetime import datetime


class EntidadBase(ABC):
    """Clase abstracta base para Cliente, Servicio y Reserva."""

    def __init__(self):
        # Guardamos la fecha de creación del objeto
        self._fecha_creacion = datetime.now()

    @property
    def fecha_creacion(self):
        return self._fecha_creacion

    @abstractmethod
    def obtener_identificador(self) -> str:
        """Método abstracto: cada entidad debe retornar su ID único."""
        pass
