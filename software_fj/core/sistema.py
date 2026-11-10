"""Controlador central de Software FJ.
Gestiona las listas en memoria de clientes, servicios y reservas sin base de datos,
aplicando manejo avanzado de excepciones (try-except-else-finally y encadenamiento).
"""

from datetime import datetime
from software_fj.logger_config import obtener_logger
from software_fj.models.cliente import Cliente
from software_fj.models.servicios import Servicio
from software_fj.models.reserva import Reserva, EstadoReserva
from software_fj.exceptions import (
    SoftwareFJException,
    ClienteInvalidoException,
    ServicioNoDisponibleException,
    ReservaInvalidaException,
    OperacionNoPermitidaException,
)

logger = obtener_logger("Sistema")


class SistemaGestionFJ:
    """Clase administradora principal del sistema. Todo se maneja en listas internas."""

    def __init__(self, nombre_empresa: str = "Software FJ"):
        self.nombre_empresa = nombre_empresa
        # Colecciones en memoria exigidas por el Anexo 3 (sin base de datos)
        self.clientes = []
        self.servicios = []
        self.reservas = []

        logger.info("Sistema %s iniciado en memoria. Listas internas listas.", self.nombre_empresa)

    # -------------------------------------------------------------------------
    # Gestión de Clientes
    # -------------------------------------------------------------------------

    def registrar_cliente(self, id_cliente: str, nombre: str, email: str, telefono: str):
        """Registra un cliente nuevo en la lista interna controlando excepciones."""
        logger.info("Intentando registrar cliente con ID: %s", id_cliente)

        try:
            # Validamos si ya existe ese ID
            if self.buscar_cliente(id_cliente) is not None:
                raise ClienteInvalidoException(
                    f"Ya existe un cliente con la identificación '{id_cliente}'."
                )

            # Creamos el objeto Cliente (sus setters aplican las validaciones)
            nuevo_cliente = Cliente(id_cliente, nombre, email, telefono)
            self.clientes.append(nuevo_cliente)
            logger.info("Cliente registrado con éxito: %s", nuevo_cliente.nombre)
            return nuevo_cliente

        except ClienteInvalidoException as e:
            # Capturamos el error de validación sin tumbar el programa
            logger.warning("No se pudo registrar el cliente [%s]: %s", id_cliente, e.mensaje)
            return None
        except Exception as e:
            logger.error("Error inesperado al registrar cliente: %s", e, exc_info=True)
            return None

    def buscar_cliente(self, id_cliente: str):
        """Busca un cliente por su ID en la lista interna."""
        for c in self.clientes:
            if c.id_cliente == id_cliente.strip():
                return c
        return None

    # -------------------------------------------------------------------------
    # Gestión de Servicios
    # -------------------------------------------------------------------------

    def registrar_servicio(self, servicio: Servicio):
        """Agrega un servicio al catálogo en memoria."""
        if not isinstance(servicio, Servicio):
            logger.error("El objeto a registrar no es un Servicio válido.")
            return False

        if self.buscar_servicio(servicio.id_servicio) is not None:
            logger.warning("El servicio con ID '%s' ya existe.", servicio.id_servicio)
            return False

        self.servicios.append(servicio)
        logger.info("Servicio registrado: %s", servicio.describir_servicio())
        return True

    def buscar_servicio(self, id_servicio: str):
        """Busca un servicio en el catálogo por su ID."""
        for s in self.servicios:
            if s.id_servicio == id_servicio.strip():
                return s
        return None

    # -------------------------------------------------------------------------
    # Transacción de Reserva con try / except / else / finally
    # -------------------------------------------------------------------------

    def crear_reserva(
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        fecha_inicio: datetime,
        duracion: float,
        descuento: float = 0.0,
        recargo_pico: float = 0.0,
        con_iva: bool = True
    ):
        """Crea una reserva aplicando el patrón completo try / except / else / finally."""
        logger.info("Iniciando creación de reserva '%s'...", id_reserva)
        reserva = None
        estado_final = "INCOMPLETA"

        try:
            # 1. Comprobamos que el ID de reserva no esté repetido
            if any(r.id_reserva == id_reserva for r in self.reservas):
                raise ReservaInvalidaException(f"Ya existe una reserva con el ID '{id_reserva}'.")

            # 2. Verificamos que el cliente exista en la lista
            cliente = self.buscar_cliente(id_cliente)
            if cliente is None:
                raise ClienteInvalidoException(f"El cliente '{id_cliente}' no está registrado.")

            # 3. Verificamos que el servicio exista en el catálogo
            servicio = self.buscar_servicio(id_servicio)
            if servicio is None:
                raise ServicioNoDisponibleException(f"El servicio '{id_servicio}' no fue encontrado.")

            if not servicio.activo:
                raise ServicioNoDisponibleException(f"El servicio '{servicio.nombre}' está desactivado.")

            # 4. Instanciamos la reserva (valida duración > 0 y stock si es equipo)
            reserva = Reserva(
                id_reserva=id_reserva,
                cliente=cliente,
                servicio=servicio,
                fecha_inicio=fecha_inicio,
                duracion=duracion,
                descuento=descuento,
                recargo_pico=recargo_pico,
                con_iva=con_iva
            )

            # Confirmamos la reserva (si es equipo descuenta una unidad del stock)
            reserva.confirmar()

        except (ClienteInvalidoException, ServicioNoDisponibleException,
                ReservaInvalidaException, OperacionNoPermitidaException) as err_negocio:
            # Capturamos excepciones propias de negocio
            estado_final = f"RECHAZADA ({err_negocio.codigo})"
            logger.warning("Reserva '%s' rechazada por regla de negocio: %s", id_reserva, err_negocio)
            reserva = None

        except Exception as err_inesperado:
            # Captura de contingencias imprevistas
            estado_final = "ERROR_SISTEMA"
            logger.error("Error imprevisto en la reserva '%s': %s", id_reserva, err_inesperado, exc_info=True)
            reserva = None

        else:
            # El bloque else solo se ejecuta si NO saltó ninguna excepción en el try
            self.reservas.append(reserva)
            estado_final = "CONFIRMADA_OK"
            logger.info("Reserva '%s' guardada con éxito en la lista interna. Total: $%.2f", id_reserva, reserva.costo_total)

        finally:
            # El bloque finally siempre se ejecuta, garantizando el registro de auditoría
            logger.info("Fin de transacción para reserva '%s' -> Resultado: [%s]", id_reserva, estado_final)

        return reserva

    # -------------------------------------------------------------------------
    # Encadenamiento de Excepciones (raise ... from ...)
    # -------------------------------------------------------------------------

    def procesar_reserva_datos_externos(
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        fecha_str: str,
        duracion_str: str
    ):
        """Procesa datos recibidos en texto con conversión explícita y encadenamiento de excepciones."""
        logger.info("Procesando datos de texto para la reserva '%s'...", id_reserva)

        try:
            # Intentamos convertir la fecha desde texto
            try:
                fecha_dt = datetime.strptime(fecha_str.strip(), "%Y-%m-%d %H:%M")
            except ValueError as err_fecha:
                # Encadenamos la excepción: lanzamos una de negocio a partir del ValueError nativo
                raise ReservaInvalidaException(
                    f"El formato de la fecha '{fecha_str}' es incorrecto. Debe ser AAAA-MM-DD HH:MM."
                ) from err_fecha

            # Intentamos convertir la duración a número flotante
            try:
                duracion_num = float(duracion_str)
            except (ValueError, TypeError) as err_num:
                # Encadenamos la excepción de duración
                raise ReservaInvalidaException(
                    f"La duración '{duracion_str}' no es un número válido."
                ) from err_num

            # Si las conversiones funcionaron, enviamos a la transacción
            return self.crear_reserva(
                id_reserva=id_reserva,
                id_cliente=id_cliente,
                id_servicio=id_servicio,
                fecha_inicio=fecha_dt,
                duracion=duracion_num
            )

        except ReservaInvalidaException as rie:
            # Registramos en el log la excepción y su causa original (__cause__)
            logger.error(
                "Excepción encadenada en reserva '%s': %s | Causa original: %s",
                id_reserva, rie, repr(rie.__cause__), exc_info=True
            )
            return None

    # -------------------------------------------------------------------------
    # Cancelación de Reservas
    # -------------------------------------------------------------------------

    def cancelar_reserva(self, id_reserva: str, motivo: str = "Solicitud del cliente"):
        """Cancela una reserva activa y gestiona las excepciones correspondientes."""
        logger.info("Solicitando cancelación de reserva: %s", id_reserva)

        try:
            reserva = self.buscar_reserva(id_reserva)
            if reserva is None:
                raise ReservaInvalidaException(f"No se encontró la reserva '{id_reserva}'.")

            # Intentamos cancelar
            reserva.cancelar(motivo=motivo)
            logger.info("Reserva '%s' cancelada correctamente. Motivo: %s", id_reserva, motivo)
            return True

        except OperacionNoPermitidaException as e:
            logger.warning("No se pudo cancelar '%s': %s", id_reserva, e.mensaje)
            return False
        except SoftwareFJException as e:
            logger.warning("Fallo en la cancelación: %s", e.mensaje)
            return False

    def buscar_reserva(self, id_reserva: str):
        """Busca una reserva por su ID en la lista interna."""
        for r in self.reservas:
            if r.id_reserva == id_reserva.strip():
                return r
        return None

    def resumen_sistema(self):
        """Genera un resumen simple del estado actual en memoria."""
        confirmadas = sum(1 for r in self.reservas if r.estado == EstadoReserva.CONFIRMADA)
        canceladas = sum(1 for r in self.reservas if r.estado == EstadoReserva.CANCELADA)
        return {
            "clientes": len(self.clientes),
            "servicios": len(self.servicios),
            "reservas_totales": len(self.reservas),
            "confirmadas": confirmadas,
            "canceladas": canceladas
        }
