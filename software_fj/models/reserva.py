"""Módulo de definición de la entidad Reserva para Software FJ.

Gestiona el ciclo de vida de una reserva (PENDIENTE, CONFIRMADA, CANCELADA),
integrando un Cliente, un Servicio, parámetros de tiempo y cálculos de costos,
e implementando reglas de validación y prevención de transiciones ilegales.

Autor: Marco Steven Rodríguez Montoya
Curso: Programación (213023) - UNAD
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from software_fj.models.base import EntidadBase
from software_fj.models.cliente import Cliente
from software_fj.models.servicios import Servicio, AlquilerEquipo
from software_fj.exceptions import (
    ReservaInvalidaException,
    OperacionNoPermitidaException,
)


class EstadoReserva(str, Enum):
    """Enumeración con los estados posibles del ciclo de vida de una reserva."""
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"


class Reserva(EntidadBase):
    """Entidad que asocia un Cliente con un Servicio durante un intervalo de tiempo.

    Aplica encapsulación rigurosa y reglas de transición de estado que impiden
    confirmaciones indebidas o re-cancelaciones erróneas.
    """

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        fecha_inicio: datetime,
        duracion: float,
        descuento: float = 0.0,
        recargo_pico: float = 0.0,
        con_iva: bool = True
    ) -> None:
        """Inicializa una nueva reserva con validaciones previas.

        Args:
            id_reserva: Código alfanumérico único de la reserva (ej. 'RES-2026-001').
            cliente: Objeto Cliente registrado y válido.
            servicio: Objeto Servicio solicitado.
            fecha_inicio: Fecha y hora de programación de la reserva.
            duracion: Cantidad de horas o días contratados (> 0).
            descuento: Porcentaje de descuento aplicable.
            recargo_pico: Recargo por horario de alta demanda.
            con_iva: Si aplica cobro de IVA.

        Raises:
            ReservaInvalidaException: Si algún parámetro resulta inconsistente.
        """
        super().__init__()

        if not id_reserva or not isinstance(id_reserva, str):
            raise ReservaInvalidaException(
                "El identificador de la reserva no puede ser vacío.",
                codigo_error="ERR_RESERVA_ID_VACIO"
            )

        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaException(
                f"El cliente debe ser una instancia válida de la clase Cliente (recibido: {type(cliente).__name__}).",
                codigo_error="ERR_RESERVA_CLIENTE_INVALIDO"
            )

        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaException(
                f"El servicio debe ser una instancia válida de la jerarquía Servicio (recibido: {type(servicio).__name__}).",
                codigo_error="ERR_RESERVA_SERVICIO_INVALIDO"
            )

        if not isinstance(fecha_inicio, datetime):
            raise ReservaInvalidaException(
                "La fecha de inicio debe ser un objeto datetime válido.",
                codigo_error="ERR_RESERVA_FECHA_INVALIDA"
            )

        if duracion <= 0:
            raise ReservaInvalidaException(
                f"La duración de la reserva debe ser estrictamente positiva (recibido: {duracion}).",
                codigo_error="ERR_RESERVA_DURACION_NEGATIVA",
                detalles={"duracion": duracion}
            )

        # Validación del propio servicio
        servicio.validar_parametros(duracion)

        self.__id_reserva: str = id_reserva.strip()
        self.__cliente: Cliente = cliente
        self.__servicio: Servicio = servicio
        self.__fecha_inicio: datetime = fecha_inicio
        self.__duracion: float = float(duracion)
        self.__descuento: float = float(descuento)
        self.__recargo_pico: float = float(recargo_pico)
        self.__con_iva: bool = con_iva
        self.__estado: EstadoReserva = EstadoReserva.PENDIENTE
        self.__motivo_cancelacion: Optional[str] = None

        # Liquidación del costo inicial
        self.__costo_total: float = servicio.calcular_costo(
            duracion=self.__duracion,
            descuento=self.__descuento,
            recargo_pico=self.__recargo_pico,
            con_iva=self.__con_iva
        )

    # -------------------------------------------------------------------------
    # Propiedades
    # -------------------------------------------------------------------------

    @property
    def id_reserva(self) -> str:
        return self.__id_reserva

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def fecha_inicio(self) -> datetime:
        return self.__fecha_inicio

    @property
    def duracion(self) -> float:
        return self.__duracion

    @property
    def estado(self) -> EstadoReserva:
        return self.__estado

    @property
    def costo_total(self) -> float:
        return self.__costo_total

    @property
    def motivo_cancelacion(self) -> Optional[str]:
        return self.__motivo_cancelacion

    def obtener_identificador(self) -> str:
        """Retorna el código de reserva."""
        return self.__id_reserva

    # -------------------------------------------------------------------------
    # Máquina de Estados y Reglas de Negocio
    # -------------------------------------------------------------------------

    def confirmar(self) -> None:
        """Confirma la reserva pasando de PENDIENTE a CONFIRMADA.

        Raises:
            OperacionNoPermitidaException: Si la reserva se encuentra cancelada.
        """
        if self.__estado == EstadoReserva.CANCELADA:
            raise OperacionNoPermitidaException(
                f"No se puede confirmar la reserva '{self.__id_reserva}' porque ya se encuentra CANCELADA.",
                codigo_error="ERR_CONFIRMAR_CANCELADA",
                detalles={"id_reserva": self.__id_reserva, "estado_actual": self.__estado.value}
            )

        if self.__estado == EstadoReserva.CONFIRMADA:
            return  # Idempotente

        # Si el servicio es de alquiler de hardware, descontamos del inventario físico
        if isinstance(self.__servicio, AlquilerEquipo):
            self.__servicio.descontar_unidad()

        self.__estado = EstadoReserva.CONFIRMADA

    def cancelar(self, motivo: str = "Solicitud de cancelación estándar") -> None:
        """Cancela la reserva y restituye inventario si corresponde.

        Raises:
            OperacionNoPermitidaException: Si la reserva ya fue cancelada con anterioridad.
        """
        if self.__estado == EstadoReserva.CANCELADA:
            raise OperacionNoPermitidaException(
                f"Operación no permitida: la reserva '{self.__id_reserva}' ya se encuentra CANCELADA.",
                codigo_error="ERR_RESERVA_YA_CANCELADA",
                detalles={"id_reserva": self.__id_reserva, "motivo_previo": self.__motivo_cancelacion}
            )

        # Si estaba confirmada y era un equipo, devolvemos la unidad a bodega
        if self.__estado == EstadoReserva.CONFIRMADA and isinstance(self.__servicio, AlquilerEquipo):
            self.__servicio.reponer_unidad()

        self.__estado = EstadoReserva.CANCELADA
        self.__motivo_cancelacion = motivo.strip()

    def __str__(self) -> str:
        """Resumen visual de la reserva."""
        return (f"Reserva[{self.__id_reserva} | Estado: {self.__estado.value} | "
                f"Cliente: {self.__cliente.nombre} | Servicio: {self.__servicio.nombre} | "
                f"Fecha: {self.__fecha_inicio.strftime('%Y-%m-%d %H:%M')} | "
                f"Total: ${self.__costo_total:,.2f}]")
