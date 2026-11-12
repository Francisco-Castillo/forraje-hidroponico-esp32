# Fase 0: aprender a cultivar (casi sin electrónica)

Estado: **plan propuesto, aún no ejecutado.** Los valores de cultivo (densidad, horas de luz, días) son referencias generales **no validadas** con este equipo: se validan con los lotes propios. Contexto: [kit-starter.md](kit-starter.md).

Planilla de registro: [templates/registro-lotes.xlsx](templates/registro-lotes.xlsx).

## Objetivo

Saber cultivar microgreens de forma consistente en casa antes de automatizar nada. Automatizar un cultivo que aún no dominas es automatizar tus errores.

## Alcance

**Sí:** estantería, luz con temporizador de enchufe, riego manual, registro de lotes y de ambiente con el sistema ya existente (ESP32, DHT11, suelo, Mosquitto, Spring Boot, TimescaleDB).

**No (todavía):** bomba, ventilación automática, energía solar, 24 V, modo autónomo con microSD. La bomba que llegue se prueba aparte según la sección 12 del artifact, sin conectarla al cultivo.

## Qué comprar o preparar

Genérico, sin marcas; confirmar disponibilidad y precio.

| Elemento | Nota |
|---|---|
| Bandejas con drenaje y bandejas sin agujeros debajo | Dos por lote: la de abajo recoge agua y permite regar por el fondo |
| Sustrato (p. ej. fibra de coco) | Usa el mismo sustrato en todos los ciclos mientras aprendes |
| Semillas aptas para germinar/microgreens: rábano, mostaza, girasol | Compra paquetes con lote identificable |
| Luz LED de espectro completo con enchufe temporizador | Mantenerla a distancia fija sobre la bandeja |
| Pulverizador y jarra medidora (mL) | Para medir el riego |
| Balanza de cocina con precisión de 1 g | Pesa semilla, cosecha y bandeja |
| Medidor de consumo de enchufe (vatímetro) | Mide kWh reales; es el dato para tu argumento de ahorro |
| Cámara del teléfono | Foto diaria desde la misma posición |

## Cómo medir

- **Ambiente:** el DHT11 va junto a las bandejas, a la altura de las plantas, **no** dentro del sustrato. Verifica antes que el ESP32 y el cable lleguen sin riesgo de salpicaduras.
- **Registro automático:** deja el stack `sensores` funcionando y anota el `DEVICE_ID`. Los datos se cruzan con la planilla **por fecha**; hoy el mensaje no trae lote ni especie.
- **Sensor de suelo:** solo calibración (ver abajo). No lo uses para decidir el riego todavía.
- **Verdad de referencia de humedad:** el peso de la bandeja. Pesa la bandeja recién regada y antes del siguiente riego.

## Plan de ciclos

Cambia **una sola variable por ciclo** y anótala en la planilla.

| Ciclo | Especie | Propósito | Variable que cambias |
|---|---|---|---|
| 1 | Rabanito | Aprender el flujo completo | Ninguna: sigue el envase de la semilla |
| 2 | Mostaza | Segunda especie, mismo método | Especie |
| 3 | Rabanito (repite) | Medir repetibilidad | Ninguna: ¿repites el resultado del ciclo 1? |
| 4 | Rabanito o mostaza | Primera comparación | Densidad de siembra **o** frecuencia de riego |
| 5 | Girasol | Especie más exigente | Remojo previo y mayor riego/ventilación |
| 6+ | Repetir la mejor receta de cada especie | Confirmar | Ninguna |

Los ciclos se pueden solapar si tienes espacio; aun así, una bandeja = un lote.

## Protocolo de un lote

**Día 0, siembra**
1. Asigna ID (L001...) y anótalo en la planilla y en la bandeja.
2. Limpia las bandejas.
3. Pesa la semilla. Densidad inicial: la indicada por el proveedor de semillas; registra lo que usaste y ajusta ciclo a ciclo.
4. Remoja solo si la especie lo pide (en general girasol) y anota las horas.
5. Humedece el sustrato, esparce la semilla, presiona suavemente. Cubre para la fase de oscuridad.
6. Pesa la bandeja y registra la fecha de siembra.

**Oscuridad (blackout)**
- Unos 2 a 4 días según especie (referencia, no validada). Anota los días reales.
- Revisa a diario sin destapar de más.

**Luz**
- Descubre cuando la semilla haya germinado y activa la luz. Pon el temporizador (referencia común: 12 a 16 h por día) y registra el horario real.
- Altura de la luz fija y anotada.

**Rutina diaria (5 minutos)**
1. Mira la bandeja y haz una foto desde la misma posición.
2. Riega por el fondo con mL medidos (o pulveriza al inicio). Anota mL, hora y método en `Diario`.
3. Pesa la bandeja si es día de medición.
4. Anota observaciones: color, altura, olor, moho.

**Cosecha**
- Cosecha cuando la mayoría tenga hojas verdaderas/cotiledones abiertos, según especie.
- Corta, pesa (g) y registra la fecha, el peso y la calidad (1 a 5) en `Lotes`. Anota costo y kWh si los mides.

## Hongos o raíces: cómo distinguirlos

Los pelos radiculares blancos y finos se confunden con moho. El moho es algodonoso, crece sobre el tallo/hojas y suele ir con olor. En duda, anótalo, saca foto y compara al día siguiente. Marca "Hongos = Sí" solo con evidencia. Esto evita decisiones erróneas sobre la humedad.

## Calibración del sensor de suelo

Solo tras 2 ciclos completos. Objetivo: tres estados del mismo sustrato y mismo sensor, misma posición y profundidad.

1. Seco (sustrato sin regar).
2. Húmedo (punto de riego que usas).
3. Saturado (recién regado por completo).

Repite 3 lecturas por estado. Anótalas en la hoja `Suelo` (cruda, mV y peso de bandeja). **No** conviertas a porcentaje hasta tener esos rangos. Si las lecturas no distinguen los estados o dispersan demasiado, concluye que el sensor no sirve para esta bandeja: es un resultado válido.

## Seguridad

- Agua y electricidad: la regleta fuera del suelo y de salpicaduras, y las bandejas por debajo del nivel de la electrónica.
- El ESP32 y el cable del DHT11 fuera del alcance del agua.
- Sin conexiones de red eléctrica caseras; solo equipos ya certificados.

## Criterios de salida de la Fase 0

Se pasa a la Fase 1 cuando, **por cada especie que quieras vender**:

- [ ] 3 ciclos seguidos con cosecha aceptable (calidad 3 o más).
- [ ] Sin hongos en esos 3 ciclos.
- [ ] Rendimiento (g cosecha / g semilla) con mínimo y máximo dentro de ±20 % de la media. Umbral **propuesto**, ajustable; la hoja `Resumen` lo calcula.
- [ ] Planilla completa al menos el 90 % de los días.
- [ ] Sabes riego (mL y frecuencia), luz (horas) y días de cada especie, con datos propios.
- [ ] Sabes costo por bandeja (semilla, sustrato, luz).

También decides, con evidencia: qué sensores aportan (¿el de suelo? ¿es necesario cambiar el DHT11?), y qué parte del trabajo diario conviene automatizar primero.

## Qué entrega la Fase 0 al resto del proyecto

- Recetas por especie para el perfil de cultivo (sección 9 del artifact).
- Un conjunto de datos reales para decidir actuadores (Fase 1) y sensores.
- Primera estimación de costo y consumo para validar el negocio (Fase 3).

## Archivos

- Planilla: `docs/templates/registro-lotes.xlsx` (hojas `Leyenda`, `Lotes`, `Diario`, `Suelo`, `Resumen`). Contiene una fila de ejemplo con valores inventados (ID `EJ-000`) que el `Resumen` ignora.
