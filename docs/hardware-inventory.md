# Inventario de hardware

Estados: **Confirmado** (lo ha indicado el usuario o se observó), **Pendiente de verificar** (dato físico aún sin confirmar, no se debe suponer) y **No seleccionado** (el componente todavía no se ha elegido).

Que el DHT11 funcione con el firmware actual no permite deducir sus datos eléctricos: los datos pendientes siguen pendientes hasta que el usuario los confirme.

## Componentes

| Componente | Dato | Estado |
|---|---|---|
| Microcontrolador | ESP32 | Confirmado |
| Placa: definición en PlatformIO | `board = esp32dev` (`platformio.ini`) | Confirmado |
| Placa: modelo físico | — | Pendiente de verificar (por identificar) |
| Sensor de temperatura y humedad | DHT11, módulo de 3 pines | Confirmado |
| Chip USB-serie de la placa | — | Pendiente de verificar (no prioritario) |
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
| Humedad de suelo: AOUT | GPIO34 (ADC1_CH6, solo entrada) | Propuesto; accesibilidad en la placa sin verificar |
| Humedad de suelo: VCC | 3V3 | Propuesto; sin conectar aún |
| Humedad de suelo: GND | GND | Propuesto; sin conectar aún |
| DHT11 orden físico de los 3 pines del módulo | — | Pendiente de verificar |
| DHT11 pin GND utilizado en la placa | — | Pendiente de verificar |

## Actuadores, alimentación y potencia

| Elemento | Estado |
|---|---|
| Actuadores (bombas, iluminación, ventilación, etc.) | No seleccionados |
| Fuentes de alimentación | No seleccionadas |
| Etapas de potencia (relés, transistores) y protecciones | No seleccionadas |
| Otros sensores (nivel de agua, etc.) | No seleccionados |

## Estado de las pruebas

| Elemento | Estado |
|---|---|
| Lectura del DHT11 en GPIO4 (`src/main.cpp`) | Implementada y compilada. Probada físicamente: el usuario confirmó que muestra lecturas en el monitor serie |
| Wi-Fi + publicación MQTT (`src/main.cpp`) | Implementada y compilada. Probada en hardware el 2026-10-29: llega al broker y se guarda en TimescaleDB. Casos de fallo (Wi-Fi caído, broker detenido, sensor desconectado, clave MQTT errónea) **sin probar** |
| Lectura del sensor de humedad de suelo (`src/moisture.cpp`) | Implementada y compilada (`pio run`). **Sin probar en hardware.** Solo Serial (raw y mV, sin calibrar); no se publica por MQTT |
| Resto del sistema | No implementado |

## Datos pendientes de verificar

- Modelo físico de la placa.
- Rango real de AOUT del sensor de suelo y confirmación de GPIO34 accesible en la placa.
- Orden físico de los pines del módulo DHT11.
- Pin GND utilizado.
- Chip USB-serie (no prioritario).
- Selección de actuadores, fuentes y etapas de potencia.
