"""Módulo base para las entidades del modelo de dominio de Software FJ.

Define la abstracción fundamental 'EntidadBase' mediante la librería abc,
estableciendo el contrato mínimo de identificación que toda entidad
debe cumplir en el sistema.

Autor: Marco Steven Rodríguez Montoya
Curso: Programación (213023) - UNAD
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class EntidadBase(ABC):
    """Clase abstracta base para todas las entidades del negocio.

    Asegura que cualquier objeto de dominio posea una marca de tiempo
    de registro y obligue a la implementación del método abstracto
    'obtener_identificador' para su indexación en memoria.
    """

    def __init__(self, fecha_registro: Optional[datetime] = None) -> None:
        """Inicializa los metadatos comunes de la entidad.

        Args:
            fecha_registro: Fecha y hora de creación; si no se provee se usa la actual.
        """
        self._fecha_registro: datetime = fecha_registro or datetime.now()

    @property
    def fecha_registro(self) -> datetime:
        """Propiedad de solo lectura para la marca temporal de creación."""
        return self._fecha_registro

    @abstractmethod
    def obtener_identificador(self) -> str:
        """Método abstracto que debe devolver la clave única de la entidad.

        Returns:
            str: Identificador único que distingue a la entidad en memoria.
        """
        pass

    def __eq__(self, otro: object) -> bool:
        """Compara la igualdad lógica de dos entidades según su identificador y tipo."""
        if not isinstance(otro, EntidadBase):
            return False
        return (self.__class__ is otro.__class__ and
                self.obtener_identificador() == otro.obtener_identificador())

    def __hash__(self) -> int:
        """Permite utilizar las entidades en colecciones basadas en hash como sets."""
        return hash((self.__class__, self.obtener_identificador()))
