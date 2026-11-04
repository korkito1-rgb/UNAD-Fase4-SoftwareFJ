"""Módulo de definición de la jerarquía de Servicios para Software FJ.

Implementa la clase abstracta 'Servicio' y las clases especializadas
'ReservaSala', 'AlquilerEquipo' y 'AsesoriaEspecializada', demostrando
polimorfismo estricto, encapsulación y simulación de sobrecarga de métodos
a través de argumentos opcionales y predeterminados.

Autor: Marco Steven Rodríguez Montoya
Curso: Programación (213023) - UNAD
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from software_fj.models.base import EntidadBase
from software_fj.exceptions import (
    ServicioNoDisponibleException,
    ReservaInvalidaException,
)


IVA_COLOMBIA: float = 0.19  # Tarifa del impuesto al valor agregado (19%)


class Servicio(EntidadBase, ABC):
    """Clase abstracta base para los servicios comercializados por Software FJ.

    Contiene los atributos generales de cualquier servicio y declara
    los métodos abstractos que cada especialidad debe sobrescribir
    con su propia lógica de negocio.
    """

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        costo_base: float,
        activo: bool = True
    ) -> None:
        """Inicializa los atributos protegidos del servicio.

        Args:
            id_servicio: Código único del servicio (ej. 'SRV-SALA-01').
            nombre: Nombre descriptivo del servicio.
            costo_base: Tarifa base monetaria del servicio (mayor o igual a cero).
            activo: Bandera que indica si el servicio se encuentra ofertable.
        """
        super().__init__()
        if not id_servicio or not isinstance(id_servicio, str):
            raise ValueError("El id_servicio debe ser una cadena no vacía.")
        if not nombre or not isinstance(nombre, str):
            raise ValueError("El nombre del servicio debe ser una cadena no vacía.")
        if costo_base < 0:
            raise ValueError("El costo base no puede ser un valor negativo.")

        self._id_servicio: str = id_servicio.strip()
        self._nombre: str = nombre.strip()
        self._costo_base: float = float(costo_base)
        self._activo: bool = activo

    # -------------------------------------------------------------------------
    # Propiedades de Acceso
    # -------------------------------------------------------------------------

    @property
    def id_servicio(self) -> str:
        """Identificador único del servicio."""
        return self._id_servicio

    @property
    def nombre(self) -> str:
        """Nombre comercial del servicio."""
        return self._nombre

    @property
    def costo_base(self) -> float:
        """Tarifa base del servicio."""
        return self._costo_base

    @property
    def activo(self) -> bool:
        """Indica si el servicio está operativo."""
        return self._activo

    @activo.setter
    def activo(self, valor: bool) -> None:
        """Modifica el estado operativo del servicio."""
        self._activo = bool(valor)

    def obtener_identificador(self) -> str:
        """Implementación del contrato de EntidadBase."""
        return self._id_servicio

    # -------------------------------------------------------------------------
    # Métodos Abstractos y Polimórficos
    # -------------------------------------------------------------------------

    @abstractmethod
    def calcular_costo(
        self,
        duracion: float = 1.0,
        descuento: float = 0.0,
        recargo_pico: float = 0.0,
        con_iva: bool = True
    ) -> float:
        """Calcula el costo total del servicio simulando sobrecarga de métodos.

        Permite múltiples firmas de cálculo según los argumentos enviados:
        1. calcular_costo() -> costo estándar por 1 hora/unidad con IVA.
        2. calcular_costo(duracion) -> costo escalado por tiempo.
        3. calcular_costo(duracion, descuento) -> con deducción porcentual.
        4. calcular_costo(duracion, descuento, recargo_pico) -> con recargo por alta demanda.
        5. calcular_costo(duracion, descuento, recargo_pico, con_iva=False) -> subtotal antes de impuestos.

        Args:
            duracion: Cantidad de horas o unidades temporales (debe ser > 0).
            descuento: Porcentaje de descuento promocional (0.0 a 1.0).
            recargo_pico: Porcentaje de recargo por horario pico (0.0 a 1.0).
            con_iva: Si es True, incluye el IVA (19%) en el cálculo final.

        Returns:
            float: Valor total liquidado del servicio.
        """
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """Genera una ficha técnica polimórfica del servicio."""
        pass

    @abstractmethod
    def validar_parametros(self, duracion: float, **kwargs: Any) -> bool:
        """Valida que los parámetros de contratación sean consistentes."""
        pass


class ReservaSala(Servicio):
    """Especialización para el alquiler de salas de juntas y conferencias."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_horaria: float,
        capacidad_personas: int,
        tiene_proyector: bool = True
    ) -> None:
        """Inicializa una sala de reuniones.

        Args:
            id_servicio: Identificador único de la sala.
            nombre: Nombre de la sala (ej. 'Sala Magna Innovación').
            tarifa_horaria: Costo por hora de ocupación.
            capacidad_personas: Aforo máximo permitido (mayor a cero).
            tiene_proyector: Indica si incluye equipo audiovisual.
        """
        super().__init__(id_servicio, nombre, costo_base=tarifa_horaria)
        if capacidad_personas <= 0:
            raise ValueError("La capacidad de la sala debe ser un entero positivo.")

        self.__capacidad_personas: int = capacidad_personas
        self.__tiene_proyector: bool = tiene_proyector
        self.__tarifa_horaria: float = float(tarifa_horaria)

    @property
    def capacidad_personas(self) -> int:
        return self.__capacidad_personas

    @property
    def tiene_proyector(self) -> bool:
        return self.__tiene_proyector

    def validar_parametros(self, duracion: float, **kwargs: Any) -> bool:
        """Valida las condiciones de reserva de la sala."""
        if duracion <= 0:
            raise ReservaInvalidaException(
                f"La duración de la reserva de la sala debe ser mayor a 0 horas (recibido: {duracion}).",
                codigo_error="ERR_SALA_DURACION_INVALIDA",
                detalles={"duracion": duracion, "sala": self._nombre}
            )
        if duracion > 24:
            raise ReservaInvalidaException(
                f"No se permite reservar una sala por más de 24 horas continuas (recibido: {duracion}).",
                codigo_error="ERR_SALA_DURACION_EXCESIVA"
            )
        return True

    def calcular_costo(
        self,
        duracion: float = 1.0,
        descuento: float = 0.0,
        recargo_pico: float = 0.0,
        con_iva: bool = True
    ) -> float:
        """Calcula el costo del alquiler de la sala con sus componentes y sobrecarga."""
        self.validar_parametros(duracion)

        # Costo base por tiempo
        costo_bruto = self.__tarifa_horaria * duracion
        # Adicional técnico por proyector si está habilitado ($15,000 COP por sesión)
        adicional_proyector = 15000.0 if self.__tiene_proyector else 0.0
        subtotal = costo_bruto + adicional_proyector

        # Aplicación de recargo y descuento
        subtotal += subtotal * recargo_pico
        subtotal -= subtotal * descuento

        if con_iva:
            return round(subtotal * (1.0 + IVA_COLOMBIA), 2)
        return round(subtotal, 2)

    def describir_servicio(self) -> str:
        """Descripción polimórfica de la sala."""
        proyector_str = "Con proyector 4K" if self.__tiene_proyector else "Sin proyector"
        return (f"[SALA] {self._nombre} | Capacidad: {self.__capacidad_personas} personas | "
                f"Tarifa: ${self.__tarifa_horaria:,.2f}/h | {proyector_str}")


class AlquilerEquipo(Servicio):
    """Especialización para el préstamo de hardware e infraestructura informática."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        costo_diario: float,
        tipo_hardware: str,
        deposito_garantia: float,
        unidades_en_inventario: int
    ) -> None:
        """Inicializa un equipo disponible para alquiler.

        Args:
            id_servicio: Identificador del catálogo de equipo.
            nombre: Descripción comercial (ej. 'Servidor Móvil Blade').
            costo_diario: Tarifa de renta base por día.
            tipo_hardware: Categoría técnica (ej. 'Portátil', 'Servidor', 'Switch').
            deposito_garantia: Depósito reembolsable de seguridad.
            unidades_en_inventario: Cantidad física disponible en bodega.
        """
        super().__init__(id_servicio, nombre, costo_base=costo_diario)
        self.__tipo_hardware: str = tipo_hardware.strip()
        self.__deposito_garantia: float = max(0.0, float(deposito_garantia))
        self.__unidades_disponibles: int = max(0, int(unidades_en_inventario))

    @property
    def tipo_hardware(self) -> str:
        return self.__tipo_hardware

    @property
    def deposito_garantia(self) -> float:
        return self.__deposito_garantia

    @property
    def unidades_disponibles(self) -> int:
        return self.__unidades_disponibles

    def validar_parametros(self, duracion: float, **kwargs: Any) -> bool:
        """Verifica disponibilidad física en bodega antes de autorizar el alquiler."""
        if duracion <= 0:
            raise ReservaInvalidaException(
                f"El periodo de alquiler debe ser al menos de 1 día (recibido: {duracion}).",
                codigo_error="ERR_EQUIPO_DURACION_INVALIDA"
            )
        if self.__unidades_disponibles <= 0:
            raise ServicioNoDisponibleException(
                f"No hay unidades disponibles en inventario para el equipo '{self._nombre}'. Stock actual: 0.",
                codigo_error="ERR_EQUIPO_SIN_STOCK",
                detalles={"equipo_id": self._id_servicio, "stock": self.__unidades_disponibles}
            )
        return True

    def descontar_unidad(self) -> None:
        """Reduce el stock disponible al confirmar un alquiler."""
        if self.__unidades_disponibles <= 0:
            raise ServicioNoDisponibleException(
                f"Inventario agotado para {self._nombre}.",
                codigo_error="ERR_EQUIPO_SIN_STOCK"
            )
        self.__unidades_disponibles -= 1

    def reponer_unidad(self) -> None:
        """Restaura una unidad al inventario tras devolución o cancelación."""
        self.__unidades_disponibles += 1

    def calcular_costo(
        self,
        duracion: float = 1.0,
        descuento: float = 0.0,
        recargo_pico: float = 0.0,
        con_iva: bool = True
    ) -> float:
        """Calcula el costo del alquiler de hardware incluyendo fianza."""
        self.validar_parametros(duracion)

        costo_alquiler = self._costo_base * duracion
        costo_alquiler += costo_alquiler * recargo_pico
        costo_alquiler -= costo_alquiler * descuento

        impuesto = (costo_alquiler * IVA_COLOMBIA) if con_iva else 0.0
        # El depósito en garantía no grava IVA según normas fiscales
        total = costo_alquiler + impuesto + self.__deposito_garantia
        return round(total, 2)

    def describir_servicio(self) -> str:
        """Descripción técnica del equipo y su disponibilidad."""
        return (f"[EQUIPO] {self._nombre} ({self.__tipo_hardware}) | "
                f"Tarifa: ${self._costo_base:,.2f}/día | Depósito: ${self.__deposito_garantia:,.2f} | "
                f"Disponibles: {self.__unidades_disponibles} uds")


class AsesoriaEspecializada(Servicio):
    """Especialización para consultoría y asesoría técnica en ingeniería."""

    MULTIPLICADORES_SENIORITY: Dict[str, float] = {
        "JUNIOR": 1.0,
        "SENIOR": 1.5,
        "MASTER": 2.2
    }

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        honorarios_hora: float,
        especialidad: str,
        seniority: str = "SENIOR"
    ) -> None:
        """Inicializa una asesoría técnica.

        Args:
            id_servicio: Identificador del servicio de consultoría.
            nombre: Nombre de la temática (ej. 'Auditoría de Ciberseguridad').
            honorarios_hora: Honorarios base por hora de consultoría.
            especialidad: Área disciplinar (ej. 'DevOps', 'Arquitectura de Software').
            seniority: Nivel de experiencia ('JUNIOR', 'SENIOR', 'MASTER').
        """
        super().__init__(id_servicio, nombre, costo_base=honorarios_hora)
        seniority_limpio = seniority.strip().upper()
        if seniority_limpio not in self.MULTIPLICADORES_SENIORITY:
            raise ValueError(f"Nivel de seniority inválido '{seniority}'. Valores válidos: {list(self.MULTIPLICADORES_SENIORITY.keys())}")

        self.__especialidad: str = especialidad.strip()
        self.__seniority: str = seniority_limpio
        self.__honorarios_hora: float = float(honorarios_hora)

    @property
    def especialidad(self) -> str:
        return self.__especialidad

    @property
    def seniority(self) -> str:
        return self.__seniority

    def validar_parametros(self, duracion: float, **kwargs: Any) -> bool:
        """Valida las horas profesionales contratadas."""
        if duracion <= 0:
            raise ReservaInvalidaException(
                f"Las horas de asesoría deben ser mayores a 0 (recibido: {duracion}).",
                codigo_error="ERR_ASESORIA_DURACION_INVALIDA"
            )
        return True

    def calcular_costo(
        self,
        duracion: float = 1.0,
        descuento: float = 0.0,
        recargo_pico: float = 0.0,
        con_iva: bool = True
    ) -> float:
        """Calcula el valor de la asesoría según el multiplicador del consultor."""
        self.validar_parametros(duracion)

        factor = self.MULTIPLICADORES_SENIORITY.get(self.__seniority, 1.0)
        costo_hora_ponderado = self.__honorarios_hora * factor
        subtotal = costo_hora_ponderado * duracion

        subtotal += subtotal * recargo_pico
        subtotal -= subtotal * descuento

        if con_iva:
            return round(subtotal * (1.0 + IVA_COLOMBIA), 2)
        return round(subtotal, 2)

    def describir_servicio(self) -> str:
        """Descripción del perfil y valor hora del consultor."""
        factor = self.MULTIPLICADORES_SENIORITY[self.__seniority]
        return (f"[ASESORÍA] {self._nombre} ({self.__especialidad}) | Nivel: {self.__seniority} (x{factor}) | "
                f"Honorarios: ${self.__honorarios_hora:,.2f}/h")
