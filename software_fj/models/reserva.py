"""Clase Reserva para Software FJ.
Controla el ciclo de vida de la reserva y las transiciones entre estados.
"""

from datetime import datetime
from software_fj.models.base import EntidadBase
from software_fj.models.cliente import Cliente
from software_fj.models.servicios import Servicio, AlquilerEquipo
from software_fj.exceptions import ReservaInvalidaException, OperacionNoPermitidaException


class EstadoReserva:
    """Constantes para los estados posibles de una reserva."""
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"


class Reserva(EntidadBase):
    """Asocia un Cliente con un Servicio contratado por un periodo de tiempo."""

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
    ):
        super().__init__()

        # Validaciones de los objetos recibidos
        if not id_reserva or not isinstance(id_reserva, str):
            raise ReservaInvalidaException("El ID de la reserva no puede estar vacío.")

        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaException("El cliente debe ser un objeto válido de tipo Cliente.")

        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaException("El servicio debe ser un objeto derivado de Servicio.")

        if not isinstance(fecha_inicio, datetime):
            raise ReservaInvalidaException("La fecha debe ser un objeto datetime válido.")

        if duracion <= 0:
            raise ReservaInvalidaException(
                f"La duración de la reserva debe ser mayor a 0 (se indicó: {duracion})."
            )

        # Validamos parámetros propios del servicio solicitado
        servicio.validar_parametros(duracion)

        self.__id_reserva = id_reserva.strip()
        self.__cliente = cliente
        self.__servicio = servicio
        self.__fecha_inicio = fecha_inicio
        self.__duracion = float(duracion)
        self.__descuento = float(descuento)
        self.__recargo_pico = float(recargo_pico)
        self.__con_iva = con_iva
        self.__estado = EstadoReserva.PENDIENTE
        self.__motivo_cancelacion = ""

        # Calculamos el costo con los parámetros dados
        self.__costo_total = servicio.calcular_costo(
            duracion=self.__duracion,
            descuento=self.__descuento,
            recargo_pico=self.__recargo_pico,
            con_iva=self.__con_iva
        )

    # --- Propiedades de lectura ---
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
    def estado(self) -> str:
        return self.__estado

    @property
    def costo_total(self) -> float:
        return self.__costo_total

    @property
    def motivo_cancelacion(self) -> str:
        return self.__motivo_cancelacion

    def obtener_identificador(self) -> str:
        return self.__id_reserva

    # --- Acciones sobre el estado de la reserva ---

    def confirmar(self):
        """Confirma la reserva. Si es alquiler de equipo, descuenta una unidad del stock."""
        if self.__estado == EstadoReserva.CANCELADA:
            raise OperacionNoPermitidaException(
                f"No se puede confirmar la reserva '{self.__id_reserva}' porque ya está CANCELADA."
            )

        if self.__estado == EstadoReserva.CONFIRMADA:
            return  # Ya estaba confirmada, no repetimos

        # Si el servicio es de hardware, descontamos del inventario
        if isinstance(self.__servicio, AlquilerEquipo):
            self.__servicio.descontar_unidad()

        self.__estado = EstadoReserva.CONFIRMADA

    def cancelar(self, motivo: str = "Cancelada por el cliente"):
        """Cancela la reserva. Si era un equipo confirmado, devuelve la unidad al stock."""
        if self.__estado == EstadoReserva.CANCELADA:
            raise OperacionNoPermitidaException(
                f"La reserva '{self.__id_reserva}' ya se encuentra CANCELADA. No se puede cancelar de nuevo."
            )

        # Devolvemos el equipo al stock si estaba confirmada
        if self.__estado == EstadoReserva.CONFIRMADA and isinstance(self.__servicio, AlquilerEquipo):
            self.__servicio.reponer_unidad()

        self.__estado = EstadoReserva.CANCELADA
        self.__motivo_cancelacion = motivo

    def __str__(self):
        return (f"Reserva {self.__id_reserva} [{self.__estado}] - Cliente: {self.__cliente.nombre} | "
                f"Servicio: {self.__servicio.nombre} | Total: ${self.__costo_total:,.2f} COP")
