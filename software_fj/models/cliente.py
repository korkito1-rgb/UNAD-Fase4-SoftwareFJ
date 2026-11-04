"""Módulo de definición de la entidad Cliente para Software FJ.

Implementa encapsulación rigurosa mediante atributos privados (__),
decoradores @property y setters con validación defensiva estricta,
lanzando ClienteInvalidoException ante cualquier dato anómalo.

Autor: Marco Steven Rodríguez Montoya
Curso: Programación (213023) - UNAD
"""

import re
from typing import Optional
from software_fj.models.base import EntidadBase
from software_fj.exceptions import ClienteInvalidoException


# Expresión regular estándar para validar correos electrónicos con @ y dominio con TLD
REGEX_EMAIL = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# Expresión regular para validar teléfonos (solo dígitos numéricos, longitud 7 a 15)
REGEX_TELEFONO = re.compile(r"^\+?[0-9]{7,15}$")


class Cliente(EntidadBase):
    """Entidad que modela un cliente en el sistema Software FJ.

    Todos sus atributos son estrictamente privados (__id_cliente, __nombre,
    __email, __telefono) y son manipulados exclusivamente mediante propiedades
    con validaciones preventivas.
    """

    def __init__(
        self,
        id_cliente: str,
        nombre: str,
        email: str,
        telefono: str
    ) -> None:
        """Inicializa un cliente invocando los setters validados.

        Args:
            id_cliente: Cédula o identificador fiscal único del cliente.
            nombre: Nombre completo del cliente o razón social.
            email: Correo electrónico válido (debe contener @ y dominio).
            telefono: Número de contacto telefónico numérico (7 a 15 dígitos).

        Raises:
            ClienteInvalidoException: Si alguno de los valores suministrados es inválido.
        """
        super().__init__()
        # Inicialización de atributos privados
        self.__id_cliente: str = ""
        self.__nombre: str = ""
        self.__email: str = ""
        self.__telefono: str = ""

        # Asignación a través de las propiedades validadas
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.email = email
        self.telefono = telefono

    # -------------------------------------------------------------------------
    # Propiedades y Setters con Validación Defensiva
    # -------------------------------------------------------------------------

    @property
    def id_cliente(self) -> str:
        """Obtiene la identificación única del cliente."""
        return self.__id_cliente

    @id_cliente.setter
    def id_cliente(self, valor: str) -> None:
        """Valida y asigna el identificador del cliente."""
        if not isinstance(valor, str) or not valor.strip():
            raise ClienteInvalidoException(
                "El identificador del cliente no puede ser vacío o nulo.",
                codigo_error="ERR_CLIENTE_ID_VACIO",
                detalles={"valor_recibido": valor}
            )
        self.__id_cliente = valor.strip()

    @property
    def nombre(self) -> str:
        """Obtiene el nombre completo del cliente."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Valida y asigna el nombre del cliente."""
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ClienteInvalidoException(
                "El nombre del cliente debe contener al menos 3 caracteres alfabéticos.",
                codigo_error="ERR_CLIENTE_NOMBRE_CORTO",
                detalles={"valor_recibido": valor}
            )
        self.__nombre = valor.strip()

    @property
    def email(self) -> str:
        """Obtiene la dirección de correo electrónico del cliente."""
        return self.__email

    @email.setter
    def email(self, valor: str) -> None:
        """Valida defensivamente el formato del correo electrónico."""
        if not isinstance(valor, str):
            raise ClienteInvalidoException(
                "El correo electrónico debe ser una cadena de texto.",
                codigo_error="ERR_CLIENTE_EMAIL_TIPO",
                detalles={"tipo": type(valor).__name__}
            )

        limpio = valor.strip()
        if not limpio:
            raise ClienteInvalidoException(
                "El correo electrónico del cliente no puede estar vacío.",
                codigo_error="ERR_CLIENTE_EMAIL_VACIO"
            )

        # Validación estructural estricta: arroba y dominio válido
        if not REGEX_EMAIL.match(limpio):
            raise ClienteInvalidoException(
                f"El formato del correo electrónico '{limpio}' no es válido. Debe contener '@' y un dominio válido.",
                codigo_error="ERR_CLIENTE_EMAIL_FORMATO",
                detalles={"email_invalido": limpio}
            )

        self.__email = limpio.lower()

    @property
    def telefono(self) -> str:
        """Obtiene el número de teléfono del cliente."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        """Valida defensivamente el número de contacto telefónico."""
        if not isinstance(valor, str):
            raise ClienteInvalidoException(
                "El teléfono debe ser suministrado como cadena numérica.",
                codigo_error="ERR_CLIENTE_TELEFONO_TIPO",
                detalles={"tipo": type(valor).__name__}
            )

        limpio = valor.strip().replace(" ", "").replace("-", "")
        if not limpio:
            raise ClienteInvalidoException(
                "El teléfono del cliente no puede estar vacío.",
                codigo_error="ERR_CLIENTE_TELEFONO_VACIO"
            )

        if not REGEX_TELEFONO.match(limpio):
            raise ClienteInvalidoException(
                f"El número de teléfono '{valor}' no es válido. Debe contener entre 7 y 15 dígitos numéricos.",
                codigo_error="ERR_CLIENTE_TELEFONO_FORMATO",
                detalles={"telefono_invalido": valor}
            )

        self.__telefono = limpio

    # -------------------------------------------------------------------------
    # Implementación de Métodos de la Clase Base
    # -------------------------------------------------------------------------

    def obtener_identificador(self) -> str:
        """Retorna el identificador único del cliente para indexación."""
        return self.__id_cliente

    def __str__(self) -> str:
        """Representación legible del cliente."""
        return f"Cliente({self.__id_cliente} - {self.__nombre} | Email: {self.__email} | Tel: {self.__telefono})"

    def __repr__(self) -> str:
        """Representación formal del objeto Cliente."""
        return (f"Cliente(id_cliente='{self.__id_cliente}', nombre='{self.__nombre}', "
                f"email='{self.__email}', telefono='{self.__telefono}')")
