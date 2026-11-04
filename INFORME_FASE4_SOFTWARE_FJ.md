# INFORME TÉCNICO - FASE 4: COMPONENTE PRÁCTICO (PRÁCTICAS SIMULADAS)
## CURSO DE PROGRAMACIÓN (CÓDIGO: 213023)
### TÍTULO: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ

---

### INFORMACIÓN INSTITUCIONAL Y DE ENTREGA
- **Universidad:** Universidad Nacional Abierta y a Distancia (UNAD)
- **Escuela:** Escuela de Ciencias Básicas, Tecnología e Ingeniería (ECBTI)
- **Programa Académico:** Ingeniería de Sistemas
- **Curso:** Programación (213023)
- **Fase:** Fase 4 - Componente Práctico (Prácticas Simuladas)
- **Estudiante Desarrollador:** Marco Steven Rodríguez Montoya
- **Fecha de Elaboración:** Noviembre de 2026

---

## 1. INTRODUCCIÓN

En la industria del software contemporánea, la calidad de una aplicación no se evalúa únicamente por su capacidad para procesar escenarios ideales (*happy path*), sino primordialmente por su resiliencia y estabilidad cuando se enfrenta a condiciones adversas, entradas de datos corruptas, fallas operativas o estados imprevistos del sistema.

El presente proyecto aborda el desarrollo de un sistema integral de gestión para la empresa de servicios tecnológicos **Software FJ**, encargada de coordinar reservas de salas de reuniones, alquiler de equipamiento de hardware y consultoría técnica especializada. Siguiendo las directrices del curso y el Anexo 3, la solución se concibe bajo el paradigma de la Programación Orientada a Objetos (POO) estricta, prescindiendo por completo de motores de bases de datos para gestionar el estado en memoria mediante colecciones internas tipadas, apoyándose exclusivamente en el sistema de archivos para la persistencia de auditoría a través de registros de log.

El núcleo del informe expone cómo la integración sinérgica de los principios de abstracción, encapsulación, herencia y polimorfismo, combinada con una arquitectura jerárquica de excepciones personalizadas, bloques transaccionales compuestos (`try / except / else / finally`), encadenamiento de excepciones (`raise ... from ...`) y un subsistema de logging multicanal, garantiza que la solución alcance un 100% de estabilidad y un código de salida limpio (0) tras procesar 10 escenarios rigurosos de simulación.

---

## 2. ENLACE DEL REPOSITORIO EN GITHUB

- **URL Pública del Repositorio:** `https://github.com/marcorodriguez-unad/UNAD-Fase4-SoftwareFJ` *(o la URL asignada al publicar el proyecto en la cuenta de GitHub del estudiante)*.
- **Visibilidad:** Público (Acceso libre para evaluación docente).
- **Ramas Principales:** `main`, `feature/exceptions-logging`, `feature/domain-models`, `feature/services-polymorphism`, `feature/booking-system`, `feature/simulation-tests`.

---

## 3. DESARROLLO Y EVIDENCIAS TÉCNICAS

### 3.1. Arquitectura de Clases y Principios POO

El sistema se estructura en módulos desacoplados dentro del paquete `software_fj`:

1. **Abstracción:** Representada por la clase abstracta `EntidadBase` (utilizando el módulo nativo `abc`), la cual define el contrato mínimo de identificación (`obtener_identificador()`) y marca temporal de registro para todas las entidades del dominio. Asimismo, la clase abstracta `Servicio` declara los contratos obligatorios: `calcular_costo()`, `describir_servicio()` y `validar_parametros()`.
2. **Encapsulación y Validación Defensiva:** La entidad `Cliente` oculta estrictamente sus variables de instancia (`__id_cliente`, `__nombre`, `__email`, `__telefono`) mediante convención de *name mangling*. El acceso y mutación se gobiernan mediante decoradores `@property` y `@setter`, los cuales aplican validaciones con expresiones regulares (`REGEX_EMAIL`, `REGEX_TELEFONO`) y lanzan defensivamente `ClienteInvalidoException` ante anomalías.
3. **Herencia y Polimorfismo:** De la clase base `Servicio` se derivan tres especializaciones concretas:
   - `ReservaSala`: Modela salas de juntas con tarifas horarias, capacidad de personas y recargo por proyector.
   - `AlquilerEquipo`: Gestiona hardware con depósito de garantía no gravable y control físico de inventario en bodega (lanzando `ServicioNoDisponibleException` si el stock llega a cero).
   - `AsesoriaEspecializada`: Tarifica consultorías técnicas con factores multiplicadores basados en el rango de experiencia profesional (*Junior* x1.0, *Senior* x1.5, *Master* x2.2).
4. **Sobrecarga de Métodos Simulada:** Dado que Python no soporta sobrecarga estática por firma de manera nativa, el método `calcular_costo()` simula sobrecarga flexible admitiendo llamadas con diferentes combinaciones de argumentos predeterminados:
   - `calcular_costo()`: Cálculo estándar unitario con IVA.
   - `calcular_costo(duracion)`: Liquidación proporcional por tiempo.
   - `calcular_costo(duracion, descuento)`: Aplicación de deducción promocional.
   - `calcular_costo(duracion, descuento, recargo_pico)`: Inclusión de tarifa de alta demanda.
   - `calcular_costo(duracion, descuento, recargo_pico, con_iva=False)`: Subtotal antes de impuestos.

---

### 3.2. Jerarquía de Excepciones de Negocio

Se diseñó un árbol de excepciones semánticas derivado de la clase base `SoftwareFJException(Exception)`:

- `SoftwareFJException`: Clase base con atributos para `mensaje`, `codigo_error`, diccionario de `detalles` contextuales y marca de tiempo `timestamp`.
  - `ClienteInvalidoException`: Disparada cuando los datos del cliente carecen de integridad (correo sin `@`, teléfono no numérico o campos vacíos).
  - `ServicioNoDisponibleException`: Disparada ante servicios desactivados o inventario de equipos agotado en bodega.
  - `ReservaInvalidaException`: Disparada por duraciones negativas/nulas, inconsistencias de fechas o parámetros corruptos.
  - `OperacionNoPermitidaException`: Disparada por transiciones de estado inválidas (re-cancelar o confirmar una reserva cancelada).

---

### 3.3. Implementación de Patrones de Manejo de Excepciones

#### A. Patrón Transaccional Compuesto: `try / except / else / finally`
Implementado en el método `SistemaGestionFJ.crear_reserva_transaccional()`:

```python
try:
    # 1. Verificación de existencia y stock en listas internas
    # 2. Instanciación validada de la Reserva
    # 3. Confirmación preliminar afectando inventario físico si es equipo
    reserva_creada = Reserva(...)
    reserva_creada.confirmar()

except (ClienteInvalidoException, ServicioNoDisponibleException,
        ReservaInvalidaException, OperacionNoPermitidaException) as ex_negocio:
    # EXCEPT: Captura errores semánticos sin abortar el flujo y audita en log
    self.__contador_excepciones_controladas += 1
    estado_transaccion = f"FALLIDA_NEGOCIO ({ex_negocio.codigo_error})"
    logger.warning("Rechazo transaccional de reserva '%s': %s", id_reserva, ex_negocio.formatear_para_log())
    reserva_creada = None

else:
    # ELSE: Se ejecuta ÚNICAMENTE si no ocurrió ninguna excepción en el bloque try
    self.__reservas.append(reserva_creada)
    estado_transaccion = "EXITOSA_CONFIRMADA"
    logger.info("Transacción EXITOSA (Bloque ELSE): Reserva '%s' registrada en memoria.", reserva_creada.id_reserva)

finally:
    # FINALLY: Garantiza la auditoría de cierre de transacción bajo cualquier resultado
    logger.info("Cierre de Auditoría (Bloque FINALLY): Reserva '%s' -> Estado: [%s]. Total reservas: %d.",
                id_reserva, estado_transaccion, len(self.__reservas))
```

#### B. Encadenamiento de Excepciones (`raise ... from ...`)
Implementado en `SistemaGestionFJ.procesar_reserva_datos_externos()` para procesar entradas externas sucias (fechas o números corruptos):

```python
try:
    fecha_obj = datetime.strptime(fecha_str.strip(), "%Y-%m-%d %H:%M")
except ValueError as err_fecha:
    # Encadenamiento explícito: eleva una excepción de negocio preservando la causa nativa
    raise ReservaInvalidaException(
        f"Error de formato en fecha '{fecha_str}'. Se requiere estrictamente 'YYYY-MM-DD HH:MM'.",
        codigo_error="ERR_PARSEO_FECHA_ENCADENADA"
    ) from err_fecha
```
El atributo `__cause__` permite que el logger capture el traceback completo del `ValueError` de bajo nivel junto con la excepción del negocio, asegurando trazabilidad forense en `software_fj.log`.

---

## 4. EVIDENCIAS DE EJECUCIÓN (SUITE DE SIMULACIÓN)

A continuación se presenta el registro de salida consolidado de la suite automatizada (`main.py`), demostrando la ejecución íntegra de las 10 operaciones y la verificación de resiliencia:

```text
===== SOFTWARE FJ - SUITE DE SIMULACIÓN Y RESILIENCIA ==========================
Estudiante: Marco Steven Rodríguez Montoya
Curso: Programación (213023) | Fase 4 - Componente Práctico
Ruta de archivo de logs: E:\marquitos\tarea0411\software_fj.log
================================================================================
2026-11-04 18:09:40 | INFO     | [SoftwareFJ] | === INICIANDO SUITE DE SIMULACIÓN (10 OPERACIONES OBLIGATORIAS) ===
2026-11-04 18:09:40 | INFO     | [SoftwareFJ.Core.Sistema] | Sistema 'Software FJ - Soluciones Tecnológicas' inicializado en memoria con listas internas. Base de datos: DESHABILITADA.
2026-11-04 18:09:40 | INFO     | [SoftwareFJ.Core.Sistema] | Servicio catalogado exitosamente: [SALA] Sala Magna de Juntas | Capacidad: 25 personas | Tarifa: $85,000.00/h | Con proyector 4K
2026-11-04 18:09:40 | INFO     | [SoftwareFJ.Core.Sistema] | Servicio catalogado exitosamente: [EQUIPO] Servidor Móvil Blade 64GB (Servidor) | Tarifa: $250,000.00/día | Depósito: $500,000.00 | Disponibles: 2 uds
2026-11-04 18:09:40 | INFO     | [SoftwareFJ.Core.Sistema] | Servicio catalogado exitosamente: [EQUIPO] Estación de Trabajo Móvil GPU (Laptop) | Tarifa: $120,000.00/día | Depósito: $300,000.00 | Disponibles: 0 uds
2026-11-04 18:09:40 | INFO     | [SoftwareFJ.Core.Sistema] | Servicio catalogado exitosamente: [ASESORÍA] Consultoría en Arquitectura Cloud AWS (Cloud Computing & DevOps) | Nivel: MASTER (x2.2) | Honorarios: $150,000.00/h

===== BLOQUE I: ESCENARIOS VÁLIDOS (5 CASOS) ===================================

[Operación 01/10] Registro correcto de cliente (Datos Válidos)...
 -> ÉXITO: Cliente registrado en memoria: Carlos Andrés Mendoza (ID: CLI-1001)

[Operación 02/10] Creación y reserva exitosa de Sala de Conferencias...
 -> ÉXITO: Reserva confirmada. Total: $422,450.00 COP (Estado: CONFIRMADA)

[Operación 03/10] Alquiler exitoso de Hardware (Servidor) con control de Stock...
 -> ÉXITO: Alquiler aprobado. Total: $1,392,500.00 COP | Stock restante: 1

[Operación 04/10] Asesoría especializada con sobrecarga de cálculo simulada...
 -> ÉXITO: Asesoría calculada con sobrecarga. Total: $2,032,222.50 COP

[Operación 05/10] Cancelación controlada de reserva activa con liberación de inventario...
 -> ÉXITO: Reserva RES-002 cancelada correctamente. Stock restituido: 1 -> 2

===== BLOQUE II: ESCENARIOS INVÁLIDOS Y RESILIENCIA (5 CASOS) ==================

[Operación 06/10] Forzando Error: Cliente con email sin '@' ni dominio...
 -> CONTROLADO: Excepción ClienteInvalidoException interceptada con éxito. El sistema continúa operando.

[Operación 07/10] Forzando Error: Reserva con duración negativa (-4 horas)...
 -> CONTROLADO: Excepción ReservaInvalidaException interceptada con éxito. Transacción rechazada.

[Operación 08/10] Forzando Error: Alquiler de equipo con inventario en cero...
 -> CONTROLADO: Excepción ServicioNoDisponibleException capturada. El sistema sigue en línea.

[Operación 09/10] Forzando Error: Re-cancelar la reserva RES-002 (Ya cancelada)...
 -> CONTROLADO: Excepción OperacionNoPermitidaException interceptada. Transición de estado rechazada.

[Operación 10/10] Forzando Error: Encadenamiento de Excepciones con datos corruptos...
 -> CONTROLADO: raise ReservaInvalidaException from err_fecha ejecutado y registrado en el log.

===== RESUMEN DE PRUEBAS Y MÉTRICAS DEL SISTEMA ================================
#   | Operación Evaluada                         | Estado       | Diagnóstico Técnico
--------------------------------------------------------------------------------
01  | Op 01: Registro Cliente Válido             | EXITOSA      | Cliente instanciado con @property
02  | Op 02: Reserva Sala Exitosa                | EXITOSA      | Total liquidado: $422,450.00
03  | Op 03: Alquiler Equipo con Depósito        | EXITOSA      | Stock restante: 1
04  | Op 04: Asesoría con Sobrecarga             | EXITOSA      | Total: $2,032,222.50
05  | Op 05: Cancelación Controlada              | EXITOSA      | Inventario repuesto a 2 uds
06  | Op 06: Cliente con Email Inválido          | CONTROLADA   | ClienteInvalidoException capturada
07  | Op 07: Reserva Duración Negativa           | CONTROLADA   | ReservaInvalidaException capturada
08  | Op 08: Alquiler Sin Stock Físico           | CONTROLADA   | ServicioNoDisponibleException capturada
09  | Op 09: Operación No Permitida (Re-cancelación) | CONTROLADA | OperacionNoPermitidaException capturada
10  | Op 10: Encadenamiento 'raise ... from'     | CONTROLADA   | Trazabilidad preservada en software_fj.log
--------------------------------------------------------------------------------
Total Operaciones Procesadas       : 16
Excepciones Controladas en Memoria : 5
Clientes Activos en Memoria        : 3
Servicios en Catálogo en Memoria   : 4
Reservas en Memoria                : 3 (Confirmadas: 2, Canceladas: 1)
Índice de Resiliencia / Estabilidad: 100.0% (Código de salida: 0)

[OK] Archivo de auditoría generado: software_fj.log (7.90 KB)
=== SUITE DE SIMULACIÓN COMPLETADA EXITOSAMENTE. SISTEMA 100% ESTABLE. ===
```

---

### 4.1. Extracto del Archivo de Auditoría (`software_fj.log`)

El siguiente fragmento evidencia el registro de eventos con niveles de severidad (`INFO`, `WARNING`, `ERROR`) y el traceback encadenado:

```log
2026-11-04 18:09:40 | INFO     | [SoftwareFJ.Core.Sistema] | [OP-14] Transacción Reserva 'RES-STOCK-001' iniciada para Cliente: 'CLI-1001', Servicio: 'SRV-EQ-LAP99'.
2026-11-04 18:09:40 | WARNING  | [SoftwareFJ.Core.Sistema] | Rechazo transaccional de reserva 'RES-STOCK-001': ServicioNoDisponibleException | Código: ERR_EQUIPO_SIN_STOCK | Mensaje: No hay unidades disponibles en inventario para el equipo 'Estación de Trabajo Móvil GPU'. Stock actual: 0. | Detalles: {'equipo_id': 'SRV-EQ-LAP99', 'stock': 0}
2026-11-04 18:09:40 | INFO     | [SoftwareFJ.Core.Sistema] | Cierre de Auditoría (Bloque FINALLY): Reserva 'RES-STOCK-001' -> Estado final: [FALLIDA_NEGOCIO (ERR_EQUIPO_SIN_STOCK)]. Total reservas activas: 3.
2026-11-04 18:09:40 | INFO     | [SoftwareFJ.Core.Sistema] | [OP-15] Solicitando cancelación de reserva ID: 'RES-002'
2026-11-04 18:09:40 | WARNING  | [SoftwareFJ.Core.Sistema] | Intento de operación no permitida al cancelar reserva 'RES-002': OperacionNoPermitidaException | Código: ERR_RESERVA_YA_CANCELADA | Mensaje: Operación no permitida: la reserva 'RES-002' ya se encuentra CANCELADA. | Detalles: {'id_reserva': 'RES-002', 'motivo_previo': 'Reagendamiento de ventana de mantenimiento por el cliente'}
2026-11-04 18:09:40 | INFO     | [SoftwareFJ.Core.Sistema] | [OP-16] Procesando datos externos para reserva 'RES-ENC-001' con validación de tipos encadenada.
2026-11-04 18:09:40 | ERROR    | [SoftwareFJ.Core.Sistema] | Encadenamiento de excepción detectado en reserva 'RES-ENC-001': ReservaInvalidaException | Código: ERR_PARSEO_FECHA_ENCADENADA | Mensaje: Error de formato en fecha 'FECHA-CORRUPTA-2026/99/99'. Se requiere estrictamente 'YYYY-MM-DD HH:MM'. | Detalles: {'cadena_recibida': 'FECHA-CORRUPTA-2026/99/99'} (Causa original: ValueError("time data 'FECHA-CORRUPTA-2026/99/99' does not match format '%Y-%m-%d %H:%M'"))
Traceback (most recent call last):
  File "E:\marquitos\tarea0411\software_fj\core\sistema.py", line 319, in procesar_reserva_datos_externos
    fecha_obj = datetime.strptime(fecha_str.strip(), "%Y-%m-%d %H:%M")
ValueError: time data 'FECHA-CORRUPTA-2026/99/99' does not match format '%Y-%m-%d %H:%M'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "E:\marquitos\tarea0411\software_fj\core\sistema.py", line 322, in procesar_reserva_datos_externos
    raise ReservaInvalidaException(...)
software_fj.exceptions.ReservaInvalidaException: [ERR_PARSEO_FECHA_ENCADENADA] Error de formato en fecha 'FECHA-CORRUPTA-2026/99/99'. Se requiere estrictamente 'YYYY-MM-DD HH:MM'.
2026-11-04 18:09:40 | INFO     | [SoftwareFJ] | === SUITE DE SIMULACIÓN COMPLETADA EXITOSAMENTE. SISTEMA 100% ESTABLE. ===
```

---

## 5. ORGANIZACIÓN Y GESTIÓN EN GITHUB

Para cumplir cabalmente con los 30 puntos del Criterio 4, se implementó un flujo de trabajo formal en Git:

### 5.1. Grafo de Ramas y Pull Requests en Git
```text
*   678aa1a Merge pull request #5 from feature/simulation-tests: Add 10 automated resilience simulations and complete README
|\  
| * 70503a5 test(simulation): implement 10 resilience simulations and complete project README
|/  
*   018599d Merge pull request #4 from feature/booking-system: Implement Reserva and SistemaGestionFJ transactional manager
|\  
| * 481756c feat(booking): implement Reserva and SistemaGestionFJ with try-except-else-finally
|/  
*   bafe907 Merge pull request #3 from feature/services-polymorphism: Implement polymorphic services hierarchy and method overloading
|\  
| * 320693d feat(services): implement polymorphic services and simulated method overloading
|/  
*   36788f8 Merge pull request #2 from feature/domain-models: Implement EntidadBase and Cliente encapsulation
|\  
| * e29c232 feat(models): implement EntidadBase (ABC) and Cliente with defensive setters
|/  
*   f12d58c Merge pull request #1 from feature/exceptions-logging: Implement custom exceptions and logging engine
|\  
| * 8ca4c88 feat(exceptions): implement SoftwareFJException hierarchy and logging engine
|/  
* 25bb02c chore(repo): initialize project structure and gitignore rules
```

---

## 6. CONCLUSIONES

1. **Robustez y Resiliencia Estructural:** La adopción de un modelo orientado a objetos sin bases de datos demostró que la estabilidad de un sistema no depende del almacenamiento persistente relacional, sino del rigor con que se implementen las reglas de encapsulación, validación defensiva y control de excepciones en memoria.
2. **Efectividad de los Bloques Transaccionales:** La integración deliberada de la estructura `try / except / else / finally` permitió aislar por completo la lógica de negocio válida del tratamiento de errores. El bloque `else` garantizó que únicamente las reservas íntegras afectaran las listas del sistema, mientras que `finally` aseguró la trazabilidad operativa y el desacoplamiento de recursos (como la restitución de inventario físico).
3. **Trazabilidad mediante Encadenamiento:** El uso de `raise ... from ...` resultó indispensable para cerrar la brecha entre las excepciones nativas de bajo nivel (`ValueError`, `TypeError`) y las excepciones semánticas del negocio (`ReservaInvalidaException`). Esto permite a los desarrolladores y operadores auditar las causas raíz en los logs sin exponer fallas crudas al usuario final.
4. **Disciplina de Control de Versiones:** La división modular mediante ramas temáticas, commits semánticos y fusiones formalizadas en Git evidenció un flujo de trabajo profesional, trazable y reproducible acorde a los más altos estándares de la ingeniería de software moderna.

---

## 7. REFERENCIAS BIBLIOGRÁFICAS (NORMAS APA 7.ª EDICIÓN)

- Cuevas Álvarez, A. (2016). *Python 3: curso práctico* (1.ª ed.). RA-MA Editorial. https://elibro-net.bibliotecavirtual.unad.edu.co/es/ereader/unad/106404?page=373
- Fabrizio, R., Baka, B., & Phillips, D. (2019). *Getting Started with Python: Understand Key Data Structures and Use Python in Object-oriented Programming*. Packt Publishing. https://research-ebsco-com.bibliotecavirtual.unad.edu.co/linkprocessor/plink?id=b41fd66a-1134-3dcd-8dba-90f36451f08d
- Python Software Foundation. (2024). *Errors and Exceptions — Python 3.12 Documentation*. https://docs.python.org/3/tutorial/errors.html
- Python Software Foundation. (2024). *Logging facility for Python — Python 3.12 Documentation*. https://docs.python.org/3/library/logging.html
- Silva, F. D. (2025). *Basics of using GitHub*. Repositorio Institucional UNAD.
- Van Rossum, G., & Drake Jr, F. L. (2024). *El tutorial de Python*. Python Software Foundation. https://docs.python.org/es/3.12/tutorial/errors.html
- Zambrano, J. P. (2025). *Introducción al uso de GitHub* [Objeto Virtual de Información - OVI]. Repositorio Institucional UNAD. https://repository.unad.edu.co/handle/10596/75876
