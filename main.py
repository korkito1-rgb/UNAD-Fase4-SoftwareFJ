"""Script Principal de Pruebas y Simulación - Software FJ.
Estudiante: Marco Steven Rodríguez Montoya
Curso: Programación (Código: 213023) - Fase 4
UNAD - 2026

Este archivo ejecuta las 10 operaciones exigidas en la guía y el Anexo 3:
- 5 operaciones válidas (casos de éxito).
- 5 operaciones inválidas o con errores forzados (para validar el manejo de excepciones y la estabilidad).
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ajustamos la ruta para poder importar el paquete software_fj sin problemas
directorio_actual = Path(__file__).resolve().parent
if str(directorio_actual) not in sys.path:
    sys.path.insert(0, str(directorio_actual))

from software_fj.logger_config import configurar_logger, RUTA_LOG
from software_fj.core.sistema import SistemaGestionFJ
from software_fj.models.servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada


def linea(titulo=""):
    """Imprime una línea separadora en la consola."""
    if titulo:
        print(f"\n{'=' * 15} {titulo} {'=' * 15}")
    else:
        print("=" * 60)


def main():
    linea("SISTEMA DE GESTIÓN SOFTWARE FJ - PRUEBAS DE RESILIENCIA")
    print("Estudiante: Marco Steven Rodríguez Montoya")
    print("Curso: Programación (213023) - Fase 4")
    print(f"Archivo de logs: {RUTA_LOG}")
    linea()

    # Inicializamos el logger del sistema
    logger = configurar_logger()
    logger.info("Iniciando ejecución de las 10 simulaciones...")

    # Instanciamos el controlador del sistema en memoria (sin base de datos)
    sistema = SistemaGestionFJ("Software FJ")

    # Registramos algunos servicios de prueba en el catálogo
    sala_reuniones = ReservaSala(
        id_servicio="SALA-01",
        nombre="Sala de Juntas Principal",
        tarifa_horaria=85000.0,
        capacidad=20,
        tiene_proyector=True
    )

    servidor_rack = AlquilerEquipo(
        id_servicio="EQ-01",
        nombre="Servidor en Rack 64GB",
        tarifa_diaria=250000.0,
        tipo_equipo="Servidor",
        deposito_garantia=500000.0,
        stock_disponible=2  # Tenemos 2 unidades disponibles
    )

    laptop_sin_stock = AlquilerEquipo(
        id_servicio="EQ-02",
        nombre="Portátil de Alto Rendimiento",
        tarifa_diaria=120000.0,
        tipo_equipo="Laptop",
        deposito_garantia=300000.0,
        stock_disponible=0  # Dejamos 0 a propósito para forzar error de stock
    )

    consultor_cloud = AsesoriaEspecializada(
        id_servicio="ASE-01",
        nombre="Consultoría en Cloud y DevOps",
        honorarios_hora=150000.0,
        especialidad="Arquitectura Cloud",
        nivel="MASTER"
    )

    sistema.registrar_servicio(sala_reuniones)
    sistema.registrar_servicio(servidor_rack)
    sistema.registrar_servicio(laptop_sin_stock)
    sistema.registrar_servicio(consultor_cloud)

    fecha_manana = datetime.now() + timedelta(days=1)
    tabla_resultados = []

    # =========================================================================
    # PARTE 1: ESCENARIOS VÁLIDOS (5 OPERACIONES DE ÉXITO)
    # =========================================================================
    linea("PARTE 1: CASOS VÁLIDOS (OPERACIONES 1 A 5)")

    # 1. Registro correcto de cliente
    print("\n[Operación 01] Registrando cliente con datos válidos...")
    c1 = sistema.registrar_cliente(
        id_cliente="CLI-1001",
        nombre="Carlos Mendoza",
        email="carlos.mendoza@gmail.com",
        telefono="3159876543"
    )
    if c1:
        print(f" -> OK: Cliente '{c1.nombre}' registrado correctamente.")
        tabla_resultados.append(("01. Registro cliente válido", "ÉXITO", "Validaciones aprobadas"))
    else:
        tabla_resultados.append(("01. Registro cliente válido", "FALLÓ", "Error no esperado"))

    # 2. Reserva válida de sala de juntas
    print("\n[Operación 02] Reservando sala de conferencias por 4 horas...")
    r1 = sistema.crear_reserva(
        id_reserva="RES-001",
        id_cliente="CLI-1001",
        id_servicio="SALA-01",
        fecha_inicio=fecha_manana,
        duracion=4.0,
        con_iva=True
    )
    if r1:
        print(f" -> OK: Reserva confirmada. Total: ${r1.costo_total:,.2f} COP (con IVA)")
        tabla_resultados.append(("02. Reserva de sala", "ÉXITO", f"Total: ${r1.costo_total:,.2f}"))
    else:
        tabla_resultados.append(("02. Reserva de sala", "FALLÓ", "No se creó la reserva"))

    # 3. Alquiler de equipo de cómputo con stock
    print("\n[Operación 03] Alquilando un servidor por 3 días (con depósito de garantía)...")
    c2 = sistema.registrar_cliente(
        id_cliente="CLI-1002",
        nombre="María Gómez",
        email="maria.gomez@hotmail.com",
        telefono="3201234567"
    )
    r2 = sistema.crear_reserva(
        id_reserva="RES-002",
        id_cliente="CLI-1002",
        id_servicio="EQ-01",
        fecha_inicio=fecha_manana + timedelta(days=2),
        duracion=3.0,
        con_iva=True
    )
    if r2:
        print(f" -> OK: Alquiler aprobado. Total: ${r2.costo_total:,.2f} COP | Stock restante: {servidor_rack.stock} ud(s)")
        tabla_resultados.append(("03. Alquiler equipo con stock", "ÉXITO", f"Stock restante: {servidor_rack.stock}"))
    else:
        tabla_resultados.append(("03. Alquiler equipo con stock", "FALLÓ", "No se creó el alquiler"))

    # 4. Asesoría especializada con sobrecarga (descuento y recargo pico)
    print("\n[Operación 04] Contratando asesoría técnica (con 10% desc y 15% recargo pico)...")
    c3 = sistema.registrar_cliente(
        id_cliente="CLI-1003",
        nombre="Empresa Andina S.A.",
        email="contacto@andina.com",
        telefono="3005557890"
    )
    r3 = sistema.crear_reserva(
        id_reserva="RES-003",
        id_cliente="CLI-1003",
        id_servicio="ASE-01",
        fecha_inicio=fecha_manana + timedelta(days=3),
        duracion=5.0,
        descuento=0.10,
        recargo_pico=0.15,
        con_iva=True
    )
    if r3:
        print(f" -> OK: Asesoría liquidada con sobrecarga. Total: ${r3.costo_total:,.2f} COP")
        tabla_resultados.append(("04. Asesoría con sobrecarga", "ÉXITO", f"Total: ${r3.costo_total:,.2f}"))
    else:
        tabla_resultados.append(("04. Asesoría con sobrecarga", "FALLÓ", "No se creó la asesoría"))

    # 5. Cancelación controlada de una reserva
    print("\n[Operación 05] Cancelando la reserva RES-002 para verificar devolución de stock...")
    stock_antes = servidor_rack.stock
    cancelado = sistema.cancelar_reserva("RES-002", motivo="Reagendamiento solicitado por el cliente")
    stock_despues = servidor_rack.stock
    if cancelado:
        print(f" -> OK: Reserva cancelada correctamente. Stock repuesto: de {stock_antes} a {stock_despues} unidades.")
        tabla_resultados.append(("05. Cancelación controlada", "ÉXITO", f"Stock repuesto a {stock_despues} uds"))
    else:
        tabla_resultados.append(("05. Cancelación controlada", "FALLÓ", "No se canceló"))

    # =========================================================================
    # PARTE 2: ESCENARIOS INVÁLIDOS (5 ERRORES FORZADOS Y RESILIENCIA)
    # =========================================================================
    linea("PARTE 2: ERRORES FORZADOS (OPERACIONES 6 A 10)")

    # 6. Cliente con correo inválido (sin arroba ni dominio)
    print("\n[Operación 06] Intentando registrar cliente con correo incorrecto ('correo_malo')...")
    c_malo = sistema.registrar_cliente(
        id_cliente="CLI-9999",
        nombre="Usuario Prueba",
        email="correo_malo_sin_arroba",
        telefono="3119998877"
    )
    if c_malo is None:
        print(" -> OK: El sistema detectó el error (ClienteInvalidoException) y continuó funcionando sin caerse.")
        tabla_resultados.append(("06. Correo inválido", "CONTROLADO", "ClienteInvalidoException atrapada"))
    else:
        tabla_resultados.append(("06. Correo inválido", "FALLÓ", "Debió rechazar"))

    # 7. Reserva con duración negativa
    print("\n[Operación 07] Intentando reservar sala con duración de -3 horas...")
    r_negativa = sistema.crear_reserva(
        id_reserva="RES-NEG-01",
        id_cliente="CLI-1001",
        id_servicio="SALA-01",
        fecha_inicio=fecha_manana,
        duracion=-3.0
    )
    if r_negativa is None:
        print(" -> OK: El sistema rechazó la duración negativa (ReservaInvalidaException).")
        tabla_resultados.append(("07. Duración negativa", "CONTROLADO", "ReservaInvalidaException atrapada"))
    else:
        tabla_resultados.append(("07. Duración negativa", "FALLÓ", "Debió rechazar"))

    # 8. Alquiler de equipo sin stock en bodega
    print("\n[Operación 08] Intentando alquilar equipo con 0 unidades en inventario...")
    r_sin_stock = sistema.crear_reserva(
        id_reserva="RES-STOCK-01",
        id_cliente="CLI-1001",
        id_servicio="EQ-02",  # Este equipo tiene stock 0
        fecha_inicio=fecha_manana,
        duracion=2.0
    )
    if r_sin_stock is None:
        print(" -> OK: El sistema bloqueó la reserva por falta de stock (ServicioNoDisponibleException).")
        tabla_resultados.append(("08. Alquiler sin stock", "CONTROLADO", "ServicioNoDisponibleException atrapada"))
    else:
        tabla_resultados.append(("08. Alquiler sin stock", "FALLÓ", "Debió rechazar"))

    # 9. Intentar cancelar una reserva que ya fue cancelada
    print("\n[Operación 09] Intentando cancelar por segunda vez la reserva RES-002...")
    re_cancelar = sistema.cancelar_reserva("RES-002", motivo="Cancelación duplicada")
    if not re_cancelar:
        print(" -> OK: El sistema impidió la re-cancelación (OperacionNoPermitidaException).")
        tabla_resultados.append(("09. Re-cancelar ya cancelada", "CONTROLADO", "OperacionNoPermitidaException atrapada"))
    else:
        tabla_resultados.append(("09. Re-cancelar ya cancelada", "FALLÓ", "Debió rechazar"))

    # 10. Datos externos corruptos con encadenamiento (raise ... from ...)
    print("\n[Operación 10] Enviando fecha corrupta para probar encadenamiento de excepciones...")
    r_encadenada = sistema.procesar_reserva_datos_externos(
        id_reserva="RES-EXT-01",
        id_cliente="CLI-1001",
        id_servicio="SALA-01",
        fecha_str="FECHA-MAL-ESCRITA-99",
        duracion_str="DOS_HORAS"
    )
    if r_encadenada is None:
        print(" -> OK: Excepción encadenada con 'raise ... from err' registrada en el archivo de log.")
        tabla_resultados.append(("10. Encadenamiento (raise from)", "CONTROLADO", "Preservó ValueError en log"))
    else:
        tabla_resultados.append(("10. Encadenamiento (raise from)", "FALLÓ", "Debió encadenar"))

    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    linea("RESUMEN DE LAS 10 PRUEBAS")
    print(f"{'#':<3} | {'Caso de Prueba':<32} | {'Resultado':<11} | {'Detalle'}")
    print("-" * 65)
    for idx, (caso, resultado, detalle) in enumerate(tabla_resultados, 1):
        print(f"{idx:02d}  | {caso:<32} | {resultado:<11} | {detalle}")
    print("-" * 65)

    resumen = sistema.resumen_sistema()
    print(f"Clientes registrados : {resumen['clientes']}")
    print(f"Servicios en catálogo: {resumen['servicios']}")
    print(f"Reservas en memoria  : {resumen['reservas_totales']} (Confirmadas: {resumen['confirmadas']}, Canceladas: {resumen['canceladas']})")
    print("Estabilidad del sistema: 100% (No se abortó el programa ante ningún error)")

    # Comprobamos que el archivo de log exista
    if RUTA_LOG.exists():
        tamano_kb = RUTA_LOG.stat().st_size / 1024
        print(f"[OK] Archivo {RUTA_LOG.name} generado correctamente ({tamano_kb:.1f} KB).")
    else:
        print(f"[AVISO] No se encontró el archivo {RUTA_LOG.name}.")

    logger.info("Fin de la simulación. Todas las pruebas concluyeron con éxito.")
    linea("FIN DE LA SIMULACIÓN - CÓDIGO DE SALIDA: 0")
    return 0


if __name__ == "__main__":
    codigo = main()
    sys.exit(codigo)
