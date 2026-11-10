"""Clase Cliente con encapsulación estricta y validaciones defensivas.
Usa atributos privados (__) y decoradores @property para proteger los datos.
"""

from software_fj.models.base import EntidadBase
from software_fj.exceptions import ClienteInvalidoException


class Cliente(EntidadBase):
    """Representa a un cliente dentro de Software FJ."""

    def __init__(self, id_cliente: str, nombre: str, email: str, telefono: str):
        super().__init__()
        # Inicializamos variables privadas
        self.__id_cliente = ""
        self.__nombre = ""
        self.__email = ""
        self.__telefono = ""

        # Usamos los setters para que pasen por las validaciones
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.email = email
        self.telefono = telefono

    # --- Métodos getter y setter para id_cliente ---
    @property
    def id_cliente(self) -> str:
        return self.__id_cliente

    @id_cliente.setter
    def id_cliente(self, valor: str):
        if not isinstance(valor, str) or not valor.strip():
            raise ClienteInvalidoException("El ID del cliente no puede estar vacío.")
        self.__id_cliente = valor.strip()

    # --- Métodos getter y setter para nombre ---
    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ClienteInvalidoException("El nombre del cliente debe tener al menos 3 letras.")
        self.__nombre = valor.strip()

    # --- Métodos getter y setter para email ---
    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor: str):
        if not isinstance(valor, str):
            raise ClienteInvalidoException("El correo debe ser un texto.")

        correo_limpio = valor.strip().lower()
        # Validación defensiva del formato de correo: debe tener @ y punto
        if "@" not in correo_limpio or "." not in correo_limpio.split("@")[-1]:
            raise ClienteInvalidoException(
                f"El correo '{valor}' no es válido. Debe contener '@' y un dominio con punto."
            )
        self.__email = correo_limpio

    # --- Métodos getter y setter para telefono ---
    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not isinstance(valor, str):
            raise ClienteInvalidoException("El teléfono debe ser un texto numérico.")

        limpio = valor.strip().replace(" ", "").replace("-", "")
        # Validamos que solo contenga dígitos y tenga entre 7 y 15 números
        if not limpio.isdigit() or len(limpio) < 7 or len(limpio) > 15:
            raise ClienteInvalidoException(
                f"El teléfono '{valor}' es inválido. Debe tener entre 7 y 15 dígitos numéricos."
            )
        self.__telefono = limpio

    def obtener_identificador(self) -> str:
        """Cumple el contrato de la clase EntidadBase."""
        return self.__id_cliente

    def __str__(self):
        return f"Cliente: {self.__nombre} (ID: {self.__id_cliente}, Email: {self.__email}, Tel: {self.__telefono})"
