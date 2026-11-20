# Inventario de hardware

Estados: **Confirmado** (lo ha indicado el usuario o se observó), **Pendiente de verificar** (dato físico aún sin confirmar, no se debe suponer) y **No seleccionado** (el componente todavía no se ha elegido).

Que el DHT11 funcione con el firmware actual no permite deducir sus datos eléctricos: los datos pendientes siguen pendientes hasta que el usuario los confirme.

## Componentes

| Componente | Dato | Estado |
|---|---|---|
| Microcontrolador | ESP32 | Confirmado |
| Placa: definición en PlatformIO | `board = esp32dev` (`platformio.ini`) | Confirmado |
| Placa: modelo físico | NodeMCU ESP32S, 38 pines, Micro-USB (indicado por el usuario el 2026-11-03; listado de venta "NodeMcu Esp32 38 Pines Micro Usb Wifi Bluetooth", código 1501) | Indicado por el usuario; sin verificar en la placa. El listado no da la asignación de pines: ver el serigrafiado |
| Placa: alimentación y niveles | 5 V por Micro-USB; E/S a 3,3 V (listado de venta) | Dato del listado, sin verificar |
| Placa: memoria | 4 MB de flash QSPI, 520 KB de SRAM, 448 KB de ROM (listado de venta) | Dato del listado, sin verificar |
| Placa: ranura microSD | El listado menciona "interfaz para tarjeta SD" como característica del chip ESP32, no como ranura en la placa; el paquete solo incluye la placa | Se necesita un módulo microSD aparte (no seleccionado) |
| Sensor de temperatura y humedad | DHT11, módulo de 3 pines | Confirmado |
| Chip USB-serie de la placa | CP2102 (listado de venta) | Dato del listado, sin verificar (no prioritario). Comprobar con `lsusb` con la placa conectada |
| Sensor de humedad de suelo | Capacitivo, analógico, 3 pines, rotulado "Moisture V2.0.0" ([compra](https://www.mercadolibre.com.ar/sensor-humedad-de-suelo-soil-tierra-indoor-moisture-gtia/up/MLAU132452889?pdp_filters=item_id:MLA2758717556&sid=purchases)) | Confirmado por el usuario |
| Humedad de suelo: orden de pines (rotulado, de izquierda a derecha, visto de frente) | GND, VCC, AOUT | Confirmado por el usuario (releer el serigrafiado de la placa antes de conectar) |
| Humedad de suelo: rango de tensión de AOUT y alimentación admitida | Listados de venta de V2.0 indican 3,3–5,5 V y salida ~0–3 V, pero las fuentes se contradicen | Pendiente de verificar (el usuario no tiene multímetro) |
| Cable USB | El primer cable no creaba el puerto serie; con otro cable aparece `/dev/ttyUSB0` y se sube el firmware | Confirmado |
| Cables del sensor | Los primeros parecían cortados por dentro (según el usuario); con otros el DHT11 responde | Confirmado por el usuario |

## Conexiones

| Conexión | Dato | Estado |
|---|---|---|
| DHT11 DATA | GPIO4 del ESP32 | Confirmado |
| DHT11 alimentación: tensión (3,3 V o 5 V) | 3,3 V (indicado por el usuario) | Confirmado por el usuario |
| Humedad de suelo: AOUT | GPIO34 (ADC1_CH6, solo entrada) | Propuesto; el pin P34 existe en la placa (foto del serigrafiado, 2026-11-03) |
| Humedad de suelo: VCC | 3V3 | Propuesto; sin conectar aún |
| Humedad de suelo: GND | GND | Propuesto; sin conectar aún |
| DHT11 orden físico de los 3 pines del módulo | — | Pendiente de verificar |
| DHT11 pin GND utilizado en la placa | — | Pendiente de verificar |

## Serigrafiado de la placa (leído de la foto del usuario, 2026-11-03)

Cara con el logo NodeMCU y la rotulación "ESP-32S V1.1", con el USB abajo. Vista por la otra cara, izquierda y derecha se invierten. "P" = GPIO.

- Columna izquierda (arriba a abajo): GND, P23, P22, TX, RX, P21, GND, P19, P18, P5, P17, P16, P4, P0, P2, P15, SD1, SD0, CLK.
- Columna derecha (arriba a abajo): 3V3, EN, SUP, SUN, P34, P35, P32, P33, P25, P26, P27, P14, P12, GND, P13, SD2, SD3, GND, 5V. El usuario confirmó que el pin antes de 5V está rotulado GND; la página de referencia (espboards.dev) pone CMD ahí. **Discrepancia sin resolver:** no usarlo como GND hasta comprobar continuidad con un GND conocido (multímetro).
- SD0 a SD3 y CLK son pines de la memoria flash: no usar.
- P4 está junto a P0 y P2 (pines de arranque): cuidar que el cable del DHT11 no toque P0 al arrancar.
- Pines propuestos para el kit (existen en la placa; conexiones **sin hacer ni verificar**): microSD por SPI en P5 (CS), P23 (MOSI), P19 (MISO), P18 (SCK); reloj RTC por I2C en P21 y P22; bomba en P26, flotador en P27 y cooler en P17.

## Actuadores, alimentación y potencia

| Elemento | Estado |
|---|---|
| Bomba de agua | Modelo JT500, 12 V DC, 15 W (etiqueta, leída por el usuario). Comprada. Prueba corta sola el 2026-11-04: gira, silenciosa, caudal fuerte (observación del usuario). Corriente sin medir. Cable amarillo: función desconocida, sin conectar | Probada sola el 2026-11-04 y con el ESP32 el 2026-11-16 (ver Estado de las pruebas) |
| Cooler (ventilador) | Genérico, 12 V DC, 2 cables, negro y blanco (indicado por el usuario el 2026-11-12). Corriente y modelo **sin verificar**. Polaridad: se montó negro (−) y blanco (+) sin leerla en etiqueta o flecha; el cooler funciona así (observación del usuario) | Indicado por el usuario; probado con el ESP32 y el MOSFET |
| MOSFET en uso en la etapa de la bomba: etiqueta **IRLZ44Z** (leída por el usuario el 2026-11-16), el que venía de la etapa del cooler. Antes figuraba como IRLZ44N; los datos de [pcb/esquematico-pcb.pdf](pcb/esquematico-pcb.pdf) son de la IRLZ44N y **no se han actualizado**. Datos de la IRLZ44Z en [conexionado-protoboard.md](conexionado-protoboard.md) | Hay otro MOSFET, que el 2026-11-16 pareció no funcionar, pero esa prueba se hizo con un cable rojo suelto en el adaptador: **no se puede concluir que esté defectuoso**; su modelo no está confirmado | Confirmado por el usuario (etiqueta); funciona con el cooler y con la bomba |
| Iluminación | Lámpara **no seleccionada**. Salida de control propuesta en GPIO25 (existe en el serigrafiado, sin conectar ni verificar). Criterios de compra pendientes de documentar |
| Fuente de 12 V y 3 A + adaptador plug a bornes | Comprados por el usuario para la bomba; sin medir con multímetro | Confirmado por el usuario |
| Otras fuentes de alimentación | No seleccionadas |
| Etapas de potencia (relés, transistores) y protecciones | No seleccionadas |
| Otros sensores (nivel de agua, etc.) | No seleccionados |
| Módulo microSD (SPI o SD_MMC) para el kit autónomo; ojo: SD_MMC de 4 bits choca con el GPIO4 del DHT11 | No seleccionado (ver [kit-starter.md](kit-starter.md)) |
| Reloj RTC (p. ej. DS3231) para la hora sin internet | No seleccionado |

## Estado de las pruebas

| Elemento | Estado |
|---|---|
| Lectura del DHT11 en GPIO4 (`src/main.cpp`) | Implementada y compilada. Probada físicamente: el usuario confirmó que muestra lecturas en el monitor serie |
| Wi-Fi + publicación MQTT (`src/main.cpp`) | Implementada y compilada. Probada en hardware el 2026-10-29: llega al broker y se guarda en TimescaleDB. Casos de fallo (Wi-Fi caído, broker detenido, sensor desconectado, clave MQTT errónea) **sin probar** |
| Lectura del sensor de humedad de suelo (`src/moisture.cpp`) | Implementada y compilada (`pio run`). **Sin probar en hardware.** Solo Serial (raw y mV, sin calibrar); no se publica por MQTT |
| Bomba JT500 alimentada sola con la fuente de 12 V (sin ESP32) | Prueba corta el 2026-11-04: gira, silenciosa, caudal fuerte (observación del usuario). Sin medir corriente ni tiempo de uso continuo |
| Bomba JT500 con el ESP32 (`src/pump.cpp`, GPIO26, tecla `p`) | Probada en hardware el 2026-11-16 (observación del usuario): con un ESP32 nuevo, MOSFET IRLZ44Z (el del cooler) y R2 de 10 kΩ, la bomba gira cuando se pulsa `p` y no arranca al enchufar. La etapa del cooler está desconectada. Sin medir corriente, calentamiento del MOSFET ni la tensión de compuerta. El firmware no se modificó. Antes de esto, las pruebas se falsearon por un cable rojo suelto del adaptador plug a bornes. El primer ESP32 dejó de responder tras un posible contacto de un cable de 12 V (sin confirmar) y se reemplazó |
| Cooler (`src/cooler.cpp`, GPIO17) | Implementado y compilado (`pio run`, 2026-11-12). Probado en hardware: el usuario confirmó que al pulsar `f` en el monitor serie el cooler funciona (observación del usuario, 2026-11-12). Tecla `f` alterna encendido/apagado, sin límite de tiempo. No se midió corriente ni calentamiento del MOSFET. Sin control automático ni MQTT |
| Luz: horario automático 20:00–06:00 UTC-3 y tecla `l` (`src/light.cpp`, GPIO25) | Implementada y compilada (`pio run`, 2026-11-20). Probada en hardware el 2026-11-20 (confirmación del usuario): con la tecla `l` un LED con resistencia de 220 Ω enciende. El horario automático **aún no se observó**; no hay lámpara ni etapa de potencia conectadas |
| Resto del sistema | No implementado |

## Datos pendientes de verificar

- Modelo físico de la placa: verificar el rotulado (el usuario indica NodeMCU ESP32S) y qué pines expone.
- Cooler: corriente real y si trae marcas de polaridad (flecha, signos) en la carcasa; funciona con el montaje actual, pero no se midió.
- Rango real de AOUT del sensor de suelo (GPIO34 existe en la placa; falta medir con multímetro).
- Orden físico de los pines del módulo DHT11.
- Pin GND utilizado.
- Chip USB-serie: el listado dice CP2102 (no prioritario).
- Pin rotulado GND junto a 5V: la página de referencia dice CMD. Comprobar continuidad con un GND conocido (ver sección de serigrafiado). También, el chip USB-serie real.
- Selección de actuadores, fuentes y etapas de potencia.
