"""Módulo central del sistema de gestión para Software FJ.

Implementa la clase controladora 'SistemaGestionFJ' que administra en memoria
(mediante listas nativas, sin base de datos) los clientes, servicios y reservas.
Aplica patrones estrictos de manejo de excepciones:
- try / except
- try / except / else
- try / except / finally
- Encadenamiento de excepciones (raise ... from ...)
- Registro continuo y estructurado de eventos en software_fj.log

Autor: Marco Steven Rodríguez Montoya
Curso: Programación (213023) - UNAD
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from software_fj.logger_config import obtener_logger
from software_fj.models.cliente import Cliente
from software_fj.models.servicios import Servicio, AlquilerEquipo
from software_fj.models.reserva import Reserva, EstadoReserva
from software_fj.exceptions import (
    SoftwareFJException,
    ClienteInvalidoException,
    ServicioNoDisponibleException,
    ReservaInvalidaException,
    OperacionNoPermitidaException,
)

logger = obtener_logger("Core.Sistema")


class SistemaGestionFJ:
    """Controlador central en memoria para el sistema Software FJ.

    No utiliza motores de bases de datos. Todo el estado reside en colecciones
    internas tipadas con validación defensiva en cada operación transaccional.
    """

    def __init__(self, nombre_empresa: str = "Software FJ S.A.S.") -> None:
        """Inicializa las listas internas en memoria y el registro de eventos.

        Args:
            nombre_empresa: Razón social del sistema.
        """
        self.__nombre_empresa: str = nombre_empresa
        self.__clientes: List[Cliente] = []
        self.__servicios: List[Servicio] = []
        self.__reservas: List[Reserva] = []
        self.__contador_operaciones: int = 0
        self.__contador_excepciones_controladas: int = 0

        logger.info(
            "Sistema '%s' inicializado en memoria con listas internas. Base de datos: DESHABILITADA.",
            self.__nombre_empresa
        )

    # -------------------------------------------------------------------------
    # Gestión de Clientes en Memoria
    # -------------------------------------------------------------------------

    def registrar_cliente(
        self,
        id_cliente: str,
        nombre: str,
        email: str,
        telefono: str
    ) -> Optional[Cliente]:
        """Registra un nuevo cliente validando unicidad y datos defensivos.

        Aplica bloque try / except para atrapar ClienteInvalidoException y
        evitar que fallos en datos suministrados aborten el hilo principal.

        Args:
            id_cliente: Documento de identidad.
            nombre: Nombre completo.
            email: Correo con formato válido.
            telefono: Número telefónico de 7 a 15 dígitos.

        Returns:
            Cliente si el registro fue exitoso; None si ocurrió un error controlado.
        """
        self.__contador_operaciones += 1
        logger.info("[OP-%02d] Iniciando registro de cliente ID: %s", self.__contador_operaciones, id_cliente)

        try:
            # Verificar si ya existe en la lista interna
            if self.buscar_cliente(id_cliente) is not None:
                raise ClienteInvalidoException(
                    f"Ya existe un cliente registrado con el identificador '{id_cliente}'.",
                    codigo_error="ERR_CLIENTE_DUPLICADO",
                    detalles={"id_cliente": id_cliente}
                )

            # Instanciación sujeta a validaciones en setters
            nuevo_cliente = Cliente(
                id_cliente=id_cliente,
                nombre=nombre,
                email=email,
                telefono=telefono
            )
            self.__clientes.append(nuevo_cliente)
            logger.info("Cliente registrado exitosamente en memoria: %s", nuevo_cliente)
            return nuevo_cliente

        except ClienteInvalidoException as cie:
            self.__contador_excepciones_controladas += 1
            logger.warning("Fallo controlado al registrar cliente: %s", cie.formatear_para_log())
            return None
        except Exception as ex_inesperada:
            self.__contador_excepciones_controladas += 1
            logger.error(
                "Excepción no esperada al procesar cliente ID '%s': %s",
                id_cliente,
                ex_inesperada,
                exc_info=True
            )
            return None

    def buscar_cliente(self, id_cliente: str) -> Optional[Cliente]:
        """Busca un cliente por su identificador en la lista interna."""
        id_normalizado = str(id_cliente).strip()
        for c in self.__clientes:
            if c.id_cliente == id_normalizado:
                return c
        return None

    # -------------------------------------------------------------------------
    # Gestión de Servicios en Memoria
    # -------------------------------------------------------------------------

    def registrar_servicio(self, servicio: Servicio) -> bool:
        """Agrega un servicio especializado al catálogo interno en memoria.

        Args:
            servicio: Instancia polimórfica de ReservaSala, AlquilerEquipo o AsesoriaEspecializada.

        Returns:
            bool: True si se registró correctamente.
        """
        self.__contador_operaciones += 1
        try:
            if not isinstance(servicio, Servicio):
                raise TypeError(f"Se esperaba una subclase de Servicio, recibido: {type(servicio).__name__}")

            if self.buscar_servicio(servicio.id_servicio) is not None:
                logger.warning("El servicio con ID '%s' ya se encuentra registrado.", servicio.id_servicio)
                return False

            self.__servicios.append(servicio)
            logger.info("Servicio catalogado exitosamente: %s", servicio.describir_servicio())
            return True

        except Exception as error_cat:
            self.__contador_excepciones_controladas += 1
            logger.error("Error al registrar servicio en catálogo: %s", error_cat, exc_info=True)
            return False

    def buscar_servicio(self, id_servicio: str) -> Optional[Servicio]:
        """Busca un servicio en la lista interna por su identificador único."""
        id_normalizado = str(id_servicio).strip()
        for s in self.__servicios:
            if s.id_servicio == id_normalizado:
                return s
        return None

    # -------------------------------------------------------------------------
    # Transacción de Reserva con try / except / else / finally
    # -------------------------------------------------------------------------

    def crear_reserva_transaccional(
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        fecha_inicio: datetime,
        duracion: float,
        descuento: float = 0.0,
        recargo_pico: float = 0.0,
        con_iva: bool = True
    ) -> Optional[Reserva]:
        """Crea una reserva aplicando rigurosamente el patrón try / except / else / finally.

        - try: Realiza las comprobaciones de existencia, reglas de stock y construcción.
        - except: Captura excepciones de negocio específicas y preserva el estado.
        - else: Se ejecuta ÚNICAMENTE si no ocurrió ninguna excepción, persistiendo la reserva en memoria.
        - finally: Se ejecuta SIEMPRE para auditar la transacción y liberar/cerrar trazas operativas.

        Returns:
            Reserva confirmada si no hubo errores; None en caso de excepciones.
        """
        self.__contador_operaciones += 1
        reserva_creada: Optional[Reserva] = None
        estado_transaccion: str = "INICIADA"

        logger.info(
            "[OP-%02d] Transacción Reserva '%s' iniciada para Cliente: '%s', Servicio: '%s'.",
            self.__contador_operaciones, id_reserva, id_cliente, id_servicio
        )

        try:
            # 1. Comprobación de unicidad de la reserva
            if any(r.id_reserva == id_reserva for r in self.__reservas):
                raise ReservaInvalidaException(
                    f"El identificador de reserva '{id_reserva}' ya existe en el sistema.",
                    codigo_error="ERR_RESERVA_DUPLICADA"
                )

            # 2. Búsqueda de cliente
            cliente = self.buscar_cliente(id_cliente)
            if cliente is None:
                raise ClienteInvalidoException(
                    f"No es posible crear la reserva: Cliente con ID '{id_cliente}' no está registrado.",
                    codigo_error="ERR_CLIENTE_NO_ENCONTRADO"
                )

            # 3. Búsqueda de servicio
            servicio = self.buscar_servicio(id_servicio)
            if servicio is None:
                raise ServicioNoDisponibleException(
                    f"No es posible crear la reserva: Servicio con ID '{id_servicio}' no existe en catálogo.",
                    codigo_error="ERR_SERVICIO_INEXISTENTE"
                )

            if not servicio.activo:
                raise ServicioNoDisponibleException(
                    f"El servicio '{servicio.nombre}' está temporalmente fuera de línea.",
                    codigo_error="ERR_SERVICIO_INACTIVO"
                )

            # 4. Creación y validación defensiva en modelo
            reserva_creada = Reserva(
                id_reserva=id_reserva,
                cliente=cliente,
                servicio=servicio,
                fecha_inicio=fecha_inicio,
                duracion=duracion,
                descuento=descuento,
                recargo_pico=recargo_pico,
                con_iva=con_iva
            )

            # Confirmar reserva preliminarmente afectando inventario si es AlquilerEquipo
            reserva_creada.confirmar()

        except (ClienteInvalidoException, ServicioNoDisponibleException,
                ReservaInvalidaException, OperacionNoPermitidaException) as ex_negocio:
            # Bloque EXCEPT: Gestión de excepciones conocidas del dominio
            self.__contador_excepciones_controladas += 1
            estado_transaccion = f"FALLIDA_NEGOCIO ({ex_negocio.codigo_error})"
            logger.warning(
                "Rechazo transaccional de reserva '%s': %s",
                id_reserva,
                ex_negocio.formatear_para_log()
            )
            reserva_creada = None

        except Exception as ex_general:
            # Bloque EXCEPT: Captura de contingencias imprevistas
            self.__contador_excepciones_controladas += 1
            estado_transaccion = f"FALLIDA_CRITICA ({type(ex_general).__name__})"
            logger.error(
                "Error crítico inesperado en reserva '%s': %s",
                id_reserva,
                ex_general,
                exc_info=True
            )
            reserva_creada = None

        else:
            # Bloque ELSE: Se ejecuta SOLO si el bloque try concluyó con éxito total
            self.__reservas.append(reserva_creada)
            estado_transaccion = "EXITOSA_CONFIRMADA"
            logger.info(
                "Transacción EXITOSA (Bloque ELSE): Reserva '%s' registrada en memoria. Costo: $%.2f COP.",
                reserva_creada.id_reserva,
                reserva_creada.costo_total
            )

        finally:
            # Bloque FINALLY: Garantiza la auditoría de cierre de transacción bajo cualquier resultado
            logger.info(
                "Cierre de Auditoría (Bloque FINALLY): Reserva '%s' -> Estado final: [%s]. Total reservas activas: %d.",
                id_reserva,
                estado_transaccion,
                len(self.__reservas)
            )

        return reserva_creada

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
    ) -> Optional[Reserva]:
        """Procesa una reserva a partir de cadenas de texto no saneadas.

        Aplica explícitamente el encadenamiento de excepciones con 'raise ... from err_origen'
        para preservar la traza del error de origen (ValueError / TypeError) dentro
        de la jerarquía de ReservaInvalidaException.
        """
        self.__contador_operaciones += 1
        logger.info(
            "[OP-%02d] Procesando datos externos para reserva '%s' con validación de tipos encadenada.",
            self.__contador_operaciones, id_reserva
        )

        try:
            # Intento de parseo de fecha con formato ISO o estándar
            try:
                fecha_obj = datetime.strptime(fecha_str.strip(), "%Y-%m-%d %H:%M")
            except ValueError as err_fecha:
                # Encadenamiento explícito de excepción de fecha
                raise ReservaInvalidaException(
                    f"Error de formato en fecha '{fecha_str}'. Se requiere estrictamente 'YYYY-MM-DD HH:MM'.",
                    codigo_error="ERR_PARSEO_FECHA_ENCADENADA",
                    detalles={"cadena_recibida": fecha_str}
                ) from err_fecha

            # Intento de casteo numérico de duración
            try:
                duracion_num = float(duracion_str)
            except (ValueError, TypeError) as err_num:
                # Encadenamiento explícito de excepción de duración
                raise ReservaInvalidaException(
                    f"El valor de duración '{duracion_str}' no es convertible a un valor numérico válido.",
                    codigo_error="ERR_PARSEO_DURACION_ENCADENADA",
                    detalles={"cadena_recibida": duracion_str}
                ) from err_num

            # Delegación a la transacción en memoria
            return self.crear_reserva_transaccional(
                id_reserva=id_reserva,
                id_cliente=id_cliente,
                id_servicio=id_servicio,
                fecha_inicio=fecha_obj,
                duracion=duracion_num
            )

        except ReservaInvalidaException as rie:
            self.__contador_excepciones_controladas += 1
            # Registrar explícitamente el encadenamiento hacia el log con traceback completo
            logger.error(
                "Encadenamiento de excepción detectado en reserva '%s': %s (Causa original: %s)",
                id_reserva,
                rie.formatear_para_log(),
                repr(rie.__cause__),
                exc_info=True
            )
            return None

    # -------------------------------------------------------------------------
    # Cancelación y Confirmación de Reservas
    # -------------------------------------------------------------------------

    def cancelar_reserva(self, id_reserva: str, motivo: str = "Solicitado por cliente") -> bool:
        """Cancela una reserva existente controlando OperacionNoPermitidaException."""
        self.__contador_operaciones += 1
        logger.info("[OP-%02d] Solicitando cancelación de reserva ID: '%s'", self.__contador_operaciones, id_reserva)

        try:
            reserva = self.buscar_reserva(id_reserva)
            if reserva is None:
                raise ReservaInvalidaException(
                    f"No existe reserva registrada con el identificador '{id_reserva}'.",
                    codigo_error="ERR_RESERVA_NO_ENCONTRADA"
                )

            reserva.cancelar(motivo=motivo)
            logger.info("Reserva '%s' cancelada satisfactoriamente. Motivo: %s", id_reserva, motivo)
            return True

        except OperacionNoPermitidaException as onpe:
            self.__contador_excepciones_controladas += 1
            logger.warning(
                "Intento de operación no permitida al cancelar reserva '%s': %s",
                id_reserva,
                onpe.formatear_para_log()
            )
            return False
        except SoftwareFJException as sfje:
            self.__contador_excepciones_controladas += 1
            logger.warning("Fallo al cancelar reserva: %s", sfje.formatear_para_log())
            return False

    def buscar_reserva(self, id_reserva: str) -> Optional[Reserva]:
        """Busca una reserva por su identificador en la lista interna."""
        id_norm = str(id_reserva).strip()
        for r in self.__reservas:
            if r.id_reserva == id_norm:
                return r
        return None

    # -------------------------------------------------------------------------
    # Métricas y Resumen del Sistema
    # -------------------------------------------------------------------------

    def obtener_metricas(self) -> Dict[str, Any]:
        """Calcula el estado y resiliencia del sistema en memoria."""
        reservas_por_estado = {
            EstadoReserva.PENDIENTE.value: 0,
            EstadoReserva.CONFIRMADA.value: 0,
            EstadoReserva.CANCELADA.value: 0,
        }
        for r in self.__reservas:
            reservas_por_estado[r.estado.value] += 1

        total_ingresos = sum(r.costo_total for r in self.__reservas if r.estado == EstadoReserva.CONFIRMADA)

        return {
            "empresa": self.__nombre_empresa,
            "total_clientes_en_memoria": len(self.__clientes),
            "total_servicios_en_catalogo": len(self.__servicios),
            "total_reservas": len(self.__reservas),
            "reservas_por_estado": reservas_por_estado,
            "total_ingresos_confirmados_cop": total_ingresos,
            "operaciones_procesadas": self.__contador_operaciones,
            "excepciones_controladas_sin_abortar": self.__contador_excepciones_controladas,
            "estabilidad_sistema_pct": 100.0  # El sistema nunca aborta el hilo principal
        }
