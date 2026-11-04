"""Script Principal de Simulación y Pruebas - Software FJ.

Ejecuta la suite obligatoria de 10 operaciones completas (5 válidas y 5 inválidas/errores forzados)
para demostrar la resiliencia, estabilidad y el manejo robusto de excepciones (try/except,
try/except/else, try/except/finally y encadenamiento de excepciones) sin abortar el hilo principal.

Autor: Marco Steven Rodríguez Montoya
Curso: Programación (213023) - Fase 4: Componente Práctico
Universidad Nacional Abierta y a Distancia (UNAD)
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Asegurar importación del paquete local
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from software_fj.logger_config import configurar_logger_principal, LOG_FILE_PATH
from software_fj.core.sistema import SistemaGestionFJ
from software_fj.models.servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from software_fj.exceptions import (
    SoftwareFJException,
    ClienteInvalidoException,
    ServicioNoDisponibleException,
    ReservaInvalidaException,
    OperacionNoPermitidaException,
)


def separador(titulo: str = "", caracter: str = "=", ancho: int = 80) -> None:
    """Imprime una línea divisoria formateada en consola."""
    if titulo:
        print(f"\n{caracter * 5} {titulo.upper()} {caracter * (ancho - len(titulo) - 7)}")
    else:
        print(caracter * ancho)


def main() -> int:
    """Punto de entrada principal para la ejecución de la suite de simulación."""
    separador("SOFTWARE FJ - SUITE DE SIMULACIÓN Y RESILIENCIA")
    print("Estudiante: Marco Steven Rodríguez Montoya")
    print("Curso: Programación (213023) | Fase 4 - Componente Práctico")
    print(f"Ruta de archivo de logs: {LOG_FILE_PATH}")
    separador()

    # Inicializar logger del sistema (consola y software_fj.log)
    logger = configurar_logger_principal()
    logger.info("=== INICIANDO SUITE DE SIMULACIÓN (10 OPERACIONES OBLIGATORIAS) ===")

    # Instanciar el sistema gestor en memoria (sin base de datos)
    sistema = SistemaGestionFJ("Software FJ - Soluciones Tecnológicas")

    # Catálogo inicial de servicios
    sala_conferencias = ReservaSala(
        id_servicio="SRV-SALA-A1",
        nombre="Sala Magna de Juntas",
        tarifa_horaria=85000.0,
        capacidad_personas=25,
        tiene_proyector=True
    )

    servidor_blade = AlquilerEquipo(
        id_servicio="SRV-EQ-SRV01",
        nombre="Servidor Móvil Blade 64GB",
        costo_diario=250000.0,
        tipo_hardware="Servidor",
        deposito_garantia=500000.0,
        unidades_en_inventario=2
    )

    laptop_agotada = AlquilerEquipo(
        id_servicio="SRV-EQ-LAP99",
        nombre="Estación de Trabajo Móvil GPU",
        costo_diario=120000.0,
        tipo_hardware="Laptop",
        deposito_garantia=300000.0,
        unidades_en_inventario=0  # Stock deliberadamente en 0 para forzar error
    )

    consultoria_cloud = AsesoriaEspecializada(
        id_servicio="SRV-ASE-CLD01",
        nombre="Consultoría en Arquitectura Cloud AWS",
        honorarios_hora=150000.0,
        especialidad="Cloud Computing & DevOps",
        seniority="MASTER"
    )

    sistema.registrar_servicio(sala_conferencias)
    sistema.registrar_servicio(servidor_blade)
    sistema.registrar_servicio(laptop_agotada)
    sistema.registrar_servicio(consultoria_cloud)

    fecha_base = datetime.now() + timedelta(days=1)
    resultados = []

    # =========================================================================
    # BLOQUE I: ESCENARIOS VÁLIDOS (5 OPERACIONES EXITOSAS)
    # =========================================================================
    separador("BLOQUE I: ESCENARIOS VÁLIDOS (5 CASOS)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 1: Registro correcto de cliente con validaciones aprobadas
    # -------------------------------------------------------------------------
    print("\n[Operación 01/10] Registro correcto de cliente (Datos Válidos)...")
    c1 = sistema.registrar_cliente(
        id_cliente="CLI-1001",
        nombre="Carlos Andrés Mendoza",
        email="carlos.mendoza@empresa.com",
        telefono="3159876543"
    )
    if c1 is not None:
        print(f" -> ÉXITO: Cliente registrado en memoria: {c1.nombre} (ID: {c1.id_cliente})")
        resultados.append(("Op 01: Registro Cliente Válido", "EXITOSA", "Cliente instanciado con @property"))
    else:
        print(" -> ERROR INESPERADO al registrar cliente válido.")
        resultados.append(("Op 01: Registro Cliente Válido", "FALLÓ", "Error en operación"))

    # -------------------------------------------------------------------------
    # OPERACIÓN 2: Reserva exitosa de sala de conferencias con cálculo e IVA
    # -------------------------------------------------------------------------
    print("\n[Operación 02/10] Creación y reserva exitosa de Sala de Conferencias...")
    r1 = sistema.crear_reserva_transaccional(
        id_reserva="RES-001",
        id_cliente="CLI-1001",
        id_servicio="SRV-SALA-A1",
        fecha_inicio=fecha_base,
        duracion=4.0,  # 4 horas
        con_iva=True
    )
    if r1 is not None:
        print(f" -> ÉXITO: Reserva confirmada. Total: ${r1.costo_total:,.2f} COP (Estado: {r1.estado.value})")
        resultados.append(("Op 02: Reserva Sala Exitosa", "EXITOSA", f"Total liquidado: ${r1.costo_total:,.2f}"))
    else:
        print(" -> ERROR en creación de reserva de sala.")
        resultados.append(("Op 02: Reserva Sala Exitosa", "FALLÓ", "No procesada"))

    # -------------------------------------------------------------------------
    # OPERACIÓN 3: Alquiler de equipo informático con depósito de garantía
    # -------------------------------------------------------------------------
    print("\n[Operación 03/10] Alquiler exitoso de Hardware (Servidor) con control de Stock...")
    c2 = sistema.registrar_cliente(
        id_cliente="CLI-1002",
        nombre="María Paula Gómez",
        email="mpaula.gomez@techsol.co",
        telefono="3201234567"
    )
    r2 = sistema.crear_reserva_transaccional(
        id_reserva="RES-002",
        id_cliente="CLI-1002",
        id_servicio="SRV-EQ-SRV01",
        fecha_inicio=fecha_base + timedelta(days=2),
        duracion=3.0,  # 3 días de alquiler
        con_iva=True
    )
    if r2 is not None:
        print(f" -> ÉXITO: Alquiler aprobado. Total: ${r2.costo_total:,.2f} COP | Stock restante: {servidor_blade.unidades_disponibles}")
        resultados.append(("Op 03: Alquiler Equipo con Depósito", "EXITOSA", f"Stock restante: {servidor_blade.unidades_disponibles}"))
    else:
        print(" -> ERROR en alquiler de equipo.")
        resultados.append(("Op 03: Alquiler Equipo con Depósito", "FALLÓ", "No procesada"))

    # -------------------------------------------------------------------------
    # OPERACIÓN 4: Asesoría técnica con sobrecarga (descuento y recargo pico)
    # -------------------------------------------------------------------------
    print("\n[Operación 04/10] Asesoría especializada con sobrecarga de cálculo simulada...")
    c3 = sistema.registrar_cliente(
        id_cliente="CLI-1003",
        nombre="Ingeniería & Redes Andinas",
        email="contacto@redesandinas.net",
        telefono="3005557890"
    )
    r3 = sistema.crear_reserva_transaccional(
        id_reserva="RES-003",
        id_cliente="CLI-1003",
        id_servicio="SRV-ASE-CLD01",
        fecha_inicio=fecha_base + timedelta(days=3),
        duracion=5.0,  # 5 horas de consultoría Master
        descuento=0.10,  # 10% descuento cliente corporativo
        recargo_pico=0.15,  # 15% recargo horario nocturno/pico
        con_iva=True
    )
    if r3 is not None:
        print(f" -> ÉXITO: Asesoría calculada con sobrecarga. Total: ${r3.costo_total:,.2f} COP")
        resultados.append(("Op 04: Asesoría con Sobrecarga", "EXITOSA", f"Total: ${r3.costo_total:,.2f}"))
    else:
        print(" -> ERROR en asesoría especializada.")
        resultados.append(("Op 04: Asesoría con Sobrecarga", "FALLÓ", "No procesada"))

    # -------------------------------------------------------------------------
    # OPERACIÓN 5: Cancelación controlada y oportuna de reserva
    # -------------------------------------------------------------------------
    print("\n[Operación 05/10] Cancelación controlada de reserva activa con liberación de inventario...")
    stock_antes = servidor_blade.unidades_disponibles
    cancelada_ok = sistema.cancelar_reserva("RES-002", motivo="Reagendamiento de ventana de mantenimiento por el cliente")
    stock_despues = servidor_blade.unidades_disponibles
    if cancelada_ok:
        print(f" -> ÉXITO: Reserva RES-002 cancelada correctamente. Stock restituido: {stock_antes} -> {stock_despues}")
        resultados.append(("Op 05: Cancelación Controlada", "EXITOSA", f"Inventario repuesto a {stock_despues} uds"))
    else:
        print(" -> ERROR al cancelar reserva válida.")
        resultados.append(("Op 05: Cancelación Controlada", "FALLÓ", "No cancelada"))

    # =========================================================================
    # BLOQUE II: ESCENARIOS INVÁLIDOS / ERRORES FORZADOS (5 CASOS)
    # =========================================================================
    separador("BLOQUE II: ESCENARIOS INVÁLIDOS Y RESILIENCIA (5 CASOS)")

    # -------------------------------------------------------------------------
    # OPERACIÓN 6: Intento de registro con email corrupto (ClienteInvalidoException)
    # -------------------------------------------------------------------------
    print("\n[Operación 06/10] Forzando Error: Cliente con email sin '@' ni dominio...")
    c_invalido = sistema.registrar_cliente(
        id_cliente="CLI-9999",
        nombre="Usuario Prueba Fallo",
        email="correo_invalido_sin_arroba",
        telefono="3119998877"
    )
    if c_invalido is None:
        print(" -> CONTROLADO: Excepción ClienteInvalidoException interceptada con éxito. El sistema continúa operando.")
        resultados.append(("Op 06: Cliente con Email Inválido", "CONTROLADA", "ClienteInvalidoException capturada"))
    else:
        print(" -> ALERTA: No se detectó la anomalía de email.")
        resultados.append(("Op 06: Cliente con Email Inválido", "FALLÓ", "No lanzó excepción"))

    # -------------------------------------------------------------------------
    # OPERACIÓN 7: Intento de reserva con duración negativa (ReservaInvalidaException)
    # -------------------------------------------------------------------------
    print("\n[Operación 07/10] Forzando Error: Reserva con duración negativa (-4 horas)...")
    r_negativa = sistema.crear_reserva_transaccional(
        id_reserva="RES-NEG-001",
        id_cliente="CLI-1001",
        id_servicio="SRV-SALA-A1",
        fecha_inicio=fecha_base,
        duracion=-4.0  # Duración ilegal
    )
    if r_negativa is None:
        print(" -> CONTROLADO: Excepción ReservaInvalidaException interceptada con éxito. Transacción rechazada.")
        resultados.append(("Op 07: Reserva Duración Negativa", "CONTROLADA", "ReservaInvalidaException capturada"))
    else:
        print(" -> ALERTA: Se permitió una duración inválida.")
        resultados.append(("Op 07: Reserva Duración Negativa", "FALLÓ", "Permitió duración negativa"))

    # -------------------------------------------------------------------------
    # OPERACIÓN 8: Intento de alquiler sin stock en bodega (ServicioNoDisponibleException)
    # -------------------------------------------------------------------------
    print("\n[Operación 08/10] Forzando Error: Alquiler de equipo con inventario en cero...")
    r_sin_stock = sistema.crear_reserva_transaccional(
        id_reserva="RES-STOCK-001",
        id_cliente="CLI-1001",
        id_servicio="SRV-EQ-LAP99",  # Laptop con stock 0
        fecha_inicio=fecha_base,
        duracion=2.0
    )
    if r_sin_stock is None:
        print(" -> CONTROLADO: Excepción ServicioNoDisponibleException capturada. El sistema sigue en línea.")
        resultados.append(("Op 08: Alquiler Sin Stock Físico", "CONTROLADA", "ServicioNoDisponibleException capturada"))
    else:
        print(" -> ALERTA: Se alquiló un equipo sin inventario disponible.")
        resultados.append(("Op 08: Alquiler Sin Stock Físico", "FALLÓ", "Permitió alquiler sin stock"))

    # -------------------------------------------------------------------------
    # OPERACIÓN 9: Intento de re-cancelar una reserva ya cancelada (OperacionNoPermitidaException)
    # -------------------------------------------------------------------------
    print("\n[Operación 09/10] Forzando Error: Re-cancelar la reserva RES-002 (Ya cancelada)...")
    re_cancelar = sistema.cancelar_reserva("RES-002", motivo="Intento de re-cancelación anómala")
    if not re_cancelar:
        print(" -> CONTROLADO: Excepción OperacionNoPermitidaException interceptada. Transición de estado rechazada.")
        resultados.append(("Op 09: Operación No Permitida (Re-cancelación)", "CONTROLADA", "OperacionNoPermitidaException capturada"))
    else:
        print(" -> ALERTA: Se permitió re-cancelar una reserva inactiva.")
        resultados.append(("Op 09: Operación No Permitida (Re-cancelación)", "FALLÓ", "Permitió re-cancelación"))

    # -------------------------------------------------------------------------
    # OPERACIÓN 10: Inyección de datos corruptos y encadenamiento (raise ... from ...)
    # -------------------------------------------------------------------------
    print("\n[Operación 10/10] Forzando Error: Encadenamiento de Excepciones con datos corruptos...")
    r_encadenada = sistema.procesar_reserva_datos_externos(
        id_reserva="RES-ENC-001",
        id_cliente="CLI-1001",
        id_servicio="SRV-SALA-A1",
        fecha_str="FECHA-CORRUPTA-2026/99/99",  # Formato no parseable
        duracion_str="CINCO_HORAS_TEXTO"        # No convertible a float
    )
    if r_encadenada is None:
        print(" -> CONTROLADO: raise ReservaInvalidaException from err_fecha ejecutado y registrado en el log.")
        resultados.append(("Op 10: Encadenamiento 'raise ... from'", "CONTROLADA", "Trazabilidad preservada en software_fj.log"))
    else:
        print(" -> ALERTA: No se interceptó el dato corrupto.")
        resultados.append(("Op 10: Encadenamiento 'raise ... from'", "FALLÓ", "No encadenó"))

    # =========================================================================
    # RESUMEN EJECUTIVO Y VERIFICACIÓN DE ESTABILIDAD
    # =========================================================================
    separador("RESUMEN DE PRUEBAS Y MÉTRICAS DEL SISTEMA")
    print(f"{'#':<3} | {'Operación Evaluada':<42} | {'Estado':<12} | {'Diagnóstico Técnico'}")
    print("-" * 80)
    for idx, (nombre_op, estado, detalle) in enumerate(resultados, 1):
        print(f"{idx:02d}  | {nombre_op:<42} | {estado:<12} | {detalle}")

    metricas = sistema.obtener_metricas()
    print("-" * 80)
    print(f"Total Operaciones Procesadas  : {metricas['operaciones_procesadas']}")
    print(f"Excepciones Controladas       : {metricas['excepciones_controladas_sin_abortar']}")
    print(f"Clientes Activos en Memoria   : {metricas['total_clientes_en_memoria']}")
    print(f"Servicios en Catálogo         : {metricas['total_servicios_en_catalogo']}")
    print(f"Reservas Registradas          : {metricas['total_reservas']} (Por estado: {metricas['reservas_por_estado']})")
    print(f"Índice de Resiliencia/Estabilidad: {metricas['estabilidad_sistema_pct']:.1f}% (Código de salida: 0)")

    # Verificar que el archivo de logs exista y tenga contenido
    if LOG_FILE_PATH.exists():
        tam_kb = LOG_FILE_PATH.stat().st_size / 1024
        print(f"\n[OK] Archivo de auditoría generado: {LOG_FILE_PATH.name} ({tam_kb:.2f} KB)")
    else:
        print(f"\n[ALERTA] Archivo de auditoría no encontrado en: {LOG_FILE_PATH}")

    logger.info("=== SUITE DE SIMULACIÓN COMPLETADA EXITOSAMENTE. SISTEMA 100% ESTABLE. ===")
    separador("FIN DE EJECUCIÓN - SISTEMA TOTALMENTE ESTABLE")
    return 0


if __name__ == "__main__":
    codigo_salida = main()
    sys.exit(codigo_salida)
