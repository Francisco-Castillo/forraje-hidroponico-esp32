# Proyecto ESP32-DHT11

## Objetivo

Desarrollar un proyecto IoT con ESP32, PlatformIO, framework Arduino y sensor DHT11.

## Rol

Actúa como desarrollador sénior especializado en ESP32, C++, PlatformIO, sensores y sistemas IoT.

El usuario es desarrollador Java backend, pero está aprendiendo electrónica e IoT. Explica los conceptos nuevos de hardware y firmware de forma sencilla.

## Reglas de trabajo

1. Antes de modificar archivos, inspecciona la estructura actual del proyecto.
2. Antes de implementar una tarea, presenta un plan breve y espera la aprobación del usuario.
3. Modifica únicamente los archivos necesarios para la tarea aprobada.
4. No sobrescribas código existente sin revisar su contenido y explicar el motivo.
5. No inventes el modelo de la placa, los pines del sensor ni las conexiones eléctricas. Pregunta si falta información.
6. Utiliza PlatformIO y el framework Arduino.
7. Declara las dependencias del proyecto en platformio.ini cuando corresponda.
8. Mantén el código sencillo, modular y fácil de mantener. Evita el sobreingeniería.
9. Después de implementar, intenta compilar el proyecto y comunica el resultado real.
10. No afirmes que el firmware funciona en el hardware si no se ha probado físicamente.
11. Explica brevemente qué archivos modificaste y por qué.
12. No ejecutes acciones destructivas ni cambies configuraciones globales sin autorización.

## Hardware

- Microcontrolador: ESP32. Definición de PlatformIO: `esp32dev`. Placa física según el usuario: NodeMCU ESP32S (sin verificar en la placa).
- Sensor: DHT11 (módulo de 3 pines).
- Conexiones confirmadas: DATA del DHT11 en GPIO4. El resto está pendiente de verificar (tensión de alimentación y orden de los pines del módulo).
- Framework: Arduino.
- Sistema de compilación: PlatformIO.

Inventario completo y estado de cada dato: `docs/hardware-inventory.md` (incluye el serigrafiado de la placa leído de una foto; discrepancia pendiente en el pin junto a 5V).

## Estado del proyecto

La lectura del DHT11 ya funciona: `src/main.cpp` lee temperatura y humedad y las muestra por el monitor serie (el usuario lo confirmó en el hardware con intervalo de 2 s). Desde 2026-11-20 el intervalo es `READ_INTERVAL_MS` = 60 s (compila; **no probado en hardware**).

Wi-Fi y publicación MQTT (Mosquitto del backend `sensores`) están implementados y compilan; el camino feliz fue probado en hardware el 2026-10-29 (llega al broker y se guarda en la base); los casos de fallo **no están probados**. Ver [docs/firmware.md](docs/firmware.md). Credenciales en `include/config.h` (no versionado; modelo `include/config.example.h`).

Actuadores: la bomba (`src/pump.cpp`, GPIO26, tecla `p`, se apaga sola a los 3 s) y el cooler (`src/cooler.cpp`, GPIO17, tecla `f`, sin límite de tiempo) se manejan a mano por el monitor serie. El cooler fue probado en hardware el 2026-11-12 (confirmación del usuario) y su etapa está hoy desconectada; la bomba fue probada con el ESP32 el 2026-11-16 (confirmación del usuario: gira al pulsar `p`; MOSFET etiquetado IRLZ44Z, con R2 de 10 kΩ; sin medir corriente ni calentamiento). Luz: `src/light.cpp` (GPIO25) con horario automático 20:00–06:00 (UTC-3) y tecla `l` manual; compila; la tecla `l` se probó en hardware el 2026-11-20 con un LED (confirmación del usuario), el horario automático **no se observó aún** y no hay lámpara ni etapa de potencia elegidas. Bomba y cooler sin control automático ni MQTT. Conexionado: [docs/conexionado-protoboard.md](docs/conexionado-protoboard.md).

## Dirección: Kit Starter autónomo (en diseño)

El usuario decidió (2026-11-03) evolucionar hacia un "Kit Starter plug & play" que funcione localmente, sin exponerse a internet: el ESP32 crea su Wi-Fi, sirve la web desde una microSD y guarda el histórico en ella. El backend Spring Boot/Mosquitto (`sensores`) **se mantiene** para desarrollo y una futura versión "pro". Es solo diseño: no hay código ni hardware nuevo, y cada paso requiere un plan aprobado. Ver [docs/kit-starter.md](docs/kit-starter.md) (riesgos incluidos) e ideas originales en `docs/ideas/`. Primera fase: cultivo manual, ver [docs/fase-0-plan.md](docs/fase-0-plan.md) (planilla en `docs/templates/registro-lotes.xlsx`).

## Agentes y skills

- Agentes en `.claude/agents/`: `iot-developer` (implementa), `iot-architect` (diseña), `electronics-technician` (revisa circuitos) y `technical-writer` (documenta).
- Skills en `.claude/skills/`: `electronics-review` y `update-documentation`.

Wi-Fi y MQTT fueron solicitados por el usuario. El Kit Starter (microSD, punto de acceso Wi-Fi, servidor web local) fue solicitado por el usuario como dirección, pero se implementa por pasos aprobados. No añadir bases de datos, aplicaciones móviles, servicios en la nube, TLS ni otra infraestructura hasta que el usuario lo solicite.