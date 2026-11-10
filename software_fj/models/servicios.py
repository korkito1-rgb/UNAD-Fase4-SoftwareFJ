"""Jerarquía de clases para los Servicios ofrecidos por Software FJ.
Implementa herencia, polimorfismo y simulación de sobrecarga de métodos.
"""

from abc import ABC, abstractmethod
from software_fj.models.base import EntidadBase
from software_fj.exceptions import ServicioNoDisponibleException, ReservaInvalidaException

# IVA general aplicable en Colombia (19%)
TASA_IVA = 0.19


class Servicio(EntidadBase, ABC):
    """Clase base abstracta para los diferentes tipos de servicios."""

    def __init__(self, id_servicio: str, nombre: str, costo_base: float, activo: bool = True):
        super().__init__()
        if not id_servicio.strip():
            raise ValueError("El ID del servicio no puede estar vacío.")
        if not nombre.strip():
            raise ValueError("El nombre del servicio no puede estar vacío.")
        if costo_base < 0:
            raise ValueError("El costo base no puede ser negativo.")

        self._id_servicio = id_servicio.strip()
        self._nombre = nombre.strip()
        self._costo_base = float(costo_base)
        self._activo = activo

    @property
    def id_servicio(self) -> str:
        return self._id_servicio

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def costo_base(self) -> float:
        return self._costo_base

    @property
    def activo(self) -> bool:
        return self._activo

    @activo.setter
    def activo(self, estado: bool):
        self._activo = bool(estado)

    def obtener_identificador(self) -> str:
        return self._id_servicio

    # -------------------------------------------------------------------------
    # Métodos abstractos que obligan al polimorfismo en las clases hijas
    # -------------------------------------------------------------------------

    @abstractmethod
    def calcular_costo(
        self,
        duracion: float = 1.0,
        descuento: float = 0.0,
        recargo_pico: float = 0.0,
        con_iva: bool = True
    ) -> float:
        """Calcula el costo del servicio.
        Simula sobrecarga de métodos en Python mediante parámetros con valores por defecto.
        """
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """Devuelve una descripción detallada según el tipo de servicio."""
        pass

    @abstractmethod
    def validar_parametros(self, duracion: float) -> bool:
        """Valida que los datos de duración y condiciones sean coherentes."""
        pass


class ReservaSala(Servicio):
    """Servicio de alquiler de salas de reuniones o conferencias."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_horaria: float,
        capacidad: int,
        tiene_proyector: bool = True
    ):
        super().__init__(id_servicio, nombre, costo_base=tarifa_horaria)
        if capacidad <= 0:
            raise ValueError("La capacidad de la sala debe ser mayor a 0 personas.")

        self.__capacidad = capacidad
        self.__tiene_proyector = tiene_proyector

    @property
    def capacidad(self) -> int:
        return self.__capacidad

    @property
    def tiene_proyector(self) -> bool:
        return self.__tiene_proyector

    def validar_parametros(self, duracion: float) -> bool:
        if duracion <= 0:
            raise ReservaInvalidaException(
                f"La duración de la reserva de la sala debe ser mayor a 0 horas (se indicó: {duracion})."
            )
        if duracion > 24:
            raise ReservaInvalidaException("No se puede reservar una sala por más de 24 horas continuas.")
        return True

    def calcular_costo(
        self,
        duracion: float = 1.0,
        descuento: float = 0.0,
        recargo_pico: float = 0.0,
        con_iva: bool = True
    ) -> float:
        # Validamos primero
        self.validar_parametros(duracion)

        # Costo según las horas
        total = self._costo_base * duracion

        # Si incluye proyector, cobramos un extra fijo de $15,000
        if self.__tiene_proyector:
            total += 15000.0

        # Aplicamos recargo por hora pico si aplica
        if recargo_pico > 0:
            total += total * recargo_pico

        # Aplicamos descuento si tiene
        if descuento > 0:
            total -= total * descuento

        # Sumamos IVA del 19% si con_iva es True
        if con_iva:
            total *= (1.0 + TASA_IVA)

        return round(total, 2)

    def describir_servicio(self) -> str:
        proyector = "Con proyector" if self.__tiene_proyector else "Sin proyector"
        return f"[Sala] {self._nombre} - Capacidad: {self.__capacidad} personas | ${self._costo_base:,.2f}/hora ({proyector})"


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos informáticos (servidores, laptops, etc.)."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_diaria: float,
        tipo_equipo: str,
        deposito_garantia: float,
        stock_disponible: int
    ):
        super().__init__(id_servicio, nombre, costo_base=tarifa_diaria)
        self.__tipo_equipo = tipo_equipo.strip()
        self.__deposito_garantia = max(0.0, float(deposito_garantia))
        self.__stock = max(0, int(stock_disponible))

    @property
    def tipo_equipo(self) -> str:
        return self.__tipo_equipo

    @property
    def deposito_garantia(self) -> float:
        return self.__deposito_garantia

    @property
    def stock(self) -> int:
        return self.__stock

    def validar_parametros(self, duracion: float) -> bool:
        if duracion <= 0:
            raise ReservaInvalidaException(
                f"El tiempo de alquiler del equipo debe ser de al menos 1 día (se indicó: {duracion})."
            )
        # Verificamos si hay inventario físico en bodega
        if self.__stock <= 0:
            raise ServicioNoDisponibleException(
                f"No hay unidades disponibles en bodega para '{self._nombre}'. Stock actual: 0."
            )
        return True

    def descontar_unidad(self):
        """Disminuye el stock cuando se confirma un alquiler."""
        if self.__stock <= 0:
            raise ServicioNoDisponibleException(f"Inventario agotado para {self._nombre}.")
        self.__stock -= 1

    def reponer_unidad(self):
        """Devuelve la unidad al stock cuando se cancela o devuelve el equipo."""
        self.__stock += 1

    def calcular_costo(
        self,
        duracion: float = 1.0,
        descuento: float = 0.0,
        recargo_pico: float = 0.0,
        con_iva: bool = True
    ) -> float:
        self.validar_parametros(duracion)

        costo_dias = self._costo_base * duracion
        if recargo_pico > 0:
            costo_dias += costo_dias * recargo_pico
        if descuento > 0:
            costo_dias -= costo_dias * descuento

        # El IVA se calcula sobre el alquiler
        iva = (costo_dias * TASA_IVA) if con_iva else 0.0

        # El depósito de garantía no lleva IVA porque es reembolsable
        total = costo_dias + iva + self.__deposito_garantia
        return round(total, 2)

    def describir_servicio(self) -> str:
        return (f"[Equipo] {self._nombre} ({self.__tipo_equipo}) | "
                f"${self._costo_base:,.2f}/día | Depósito: ${self.__deposito_garantia:,.2f} | Stock: {self.__stock} uds")


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría o consultoría técnica especializada."""

    # Multiplicador según el nivel del profesional
    FACTORES_NIVEL = {
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
        nivel: str = "SENIOR"
    ):
        super().__init__(id_servicio, nombre, costo_base=honorarios_hora)
        nivel_upper = nivel.strip().upper()
        if nivel_upper not in self.FACTORES_NIVEL:
            raise ValueError(f"Nivel no reconocido: {nivel}. Opciones: JUNIOR, SENIOR, MASTER.")

        self.__especialidad = especialidad.strip()
        self.__nivel = nivel_upper

    @property
    def especialidad(self) -> str:
        return self.__especialidad

    @property
    def nivel(self) -> str:
        return self.__nivel

    def validar_parametros(self, duracion: float) -> bool:
        if duracion <= 0:
            raise ReservaInvalidaException(
                f"Las horas de asesoría deben ser mayores a 0 (se indicó: {duracion})."
            )
        return True

    def calcular_costo(
        self,
        duracion: float = 1.0,
        descuento: float = 0.0,
        recargo_pico: float = 0.0,
        con_iva: bool = True
    ) -> float:
        self.validar_parametros(duracion)

        # Multiplicamos la tarifa base por el factor de experiencia
        factor = self.FACTORES_NIVEL[self.__nivel]
        tarifa_real = self._costo_base * factor
        subtotal = tarifa_real * duracion

        if recargo_pico > 0:
            subtotal += subtotal * recargo_pico
        if descuento > 0:
            subtotal -= subtotal * descuento

        if con_iva:
            subtotal *= (1.0 + TASA_IVA)

        return round(subtotal, 2)

    def describir_servicio(self) -> str:
        factor = self.FACTORES_NIVEL[self.__nivel]
        return (f"[Asesoría] {self._nombre} ({self.__especialidad}) | Nivel: {self.__nivel} (x{factor}) | "
                f"${self._costo_base:,.2f}/hora")
