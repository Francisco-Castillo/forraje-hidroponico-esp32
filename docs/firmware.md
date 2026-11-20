# Firmware: Wi-Fi y publicación MQTT

Estado: implementado y **compilado** (`pio run`). **Probado en hardware (2026-10-29)** el camino feliz: Wi-Fi, NTP, MQTT con autenticación, publicación al Mosquitto del backend y fila en TimescaleDB. **Sin probar** los casos de fallo.

Contrato de referencia (fuente de verdad): `docs/mqtt-contract.md` del backend `sensores`.

## Configuración

1. Copiar `include/config.example.h` a `include/config.h` (ignorado por git) y rellenar Wi-Fi, `MQTT_HOST`, `MQTT_PORT`, `MQTT_USER`, `MQTT_PASSWORD`, `DEVICE_ID` y `READ_INTERVAL_MS` (60000 ms = 1 min; el DHT11 admite como mínimo 2000 ms, pero el ambiente cambia lento y publicar tan seguido solo llena la base).
2. `MQTT_HOST` debe ser la IP LAN del PC con Docker; `localhost` apuntaría al propio ESP32. El firewall debe permitir el puerto 1883.
3. El tópico se deriva: `fvh/<DEVICE_ID>/lecturas`. `DEVICE_ID` (`[a-z0-9-]`, 1–32) es también `deviceId` y `clientId`.

## Comportamiento

- Se lee el DHT11 (GPIO4) cada `READ_INTERVAL_MS` (60 s por defecto; la primera lectura tras arrancar ocurre a los 60 s) y se muestra por Serial. Solo si la lectura es válida, hay hora válida y MQTT está conectado, se publica.
- `messageId` = `<DEVICE_ID>-<bootId hex>-<contador>`. `bootId` es aleatorio en cada arranque; no depende del reloj.
- `timestamp`: UTC con `Z`, tomado de NTP (`pool.ntp.org`, `time.google.com`) en el instante de la lectura. Si la hora es anterior a 2024-01-01 (NTP aún sin sincronizar) no se publica.
- Reconexión de Wi-Fi y MQTT no bloqueante con espera creciente (1 s a 30 s). No se reinicia el ESP32 por errores de red.

## Humedad de suelo (etapa 2, opción A)

- Sensor capacitivo en GPIO34 (`src/moisture.cpp`). Cada ciclo se muestra por Serial el valor crudo y los mV, **sin calibrar: no es un porcentaje**.
- Cada mensaje incluye el campo opcional `measurements.soilMoistureRaw` (entero 0–4095, promedio de 16 lecturas del ADC). Tópico y campos del DHT11 no cambian.
- El backend lo valida (entero 0–4095, opcional) y lo guarda en `lecturas.humedad_suelo_raw` (migración `V4`); la API lo devuelve como `soilMoistureRaw`. Verificado el 2026-10-29 con el ESP32 real: filas con valores ~3245.
- Si el DHT11 falla no se publica nada (también se pierde la lectura del suelo).
- Lectura inválida (2026-11-20, **compila; no probado en hardware**): si el promedio de las 16 muestras es 0, el campo `soilMoistureRaw` se omite del mensaje (el backend lo guarda como nulo y el frontend muestra "Sin datos"). Un capacitivo sano no llega a 0 V ni en agua (~1 V), así que un 0 indica pin flotando o sensor sin alimentación. Motivo: el 2026-11-20 se vieron en la base saltos entre 0 y ~3700 (el usuario reportó que marcaba 0 por momentos y de golpe ~3260; no se registró en qué condición estaba el sensor). Esto **no corrige el cableado**: solo evita guardar ese dato como medición. Por el monitor serie se imprime además el mínimo y el máximo de las 16 muestras para distinguir ruido de pérdida de señal.
- Estado: compilado y probado en el ESP32 el 2026-10-29 (camino feliz: publica, llega al broker y se guarda). Casos de fallo sin probar; el valor sigue **sin calibrar**.

## Diferencias con el contrato

- **QoS 0**: PubSubClient no publica con QoS 1; el contrato pide QoS 1. Un mensaje puede perderse sin aviso. Aceptado para la primera versión.
- Sin búfer offline: las lecturas durante una caída de red o sin hora NTP se descartan.
- Se usan usuario y contraseña MQTT porque el broker tiene `allow_anonymous false`. Sin TLS.

## Pruebas pendientes

Camino feliz ya verificado (publicación recibida con `mosquitto_sub` y filas en `lecturas` con el backend en marcha). Quedan los fallos (Wi-Fi caído, broker detenido, sensor desconectado, clave MQTT errónea).
