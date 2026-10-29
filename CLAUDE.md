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

- Microcontrolador: ESP32. Definición de PlatformIO: `esp32dev`. El modelo físico exacto está pendiente de verificar.
- Sensor: DHT11 (módulo de 3 pines).
- Conexiones confirmadas: DATA del DHT11 en GPIO4. El resto está pendiente de verificar (tensión de alimentación y orden de los pines del módulo).
- Framework: Arduino.
- Sistema de compilación: PlatformIO.

Inventario completo y estado de cada dato: `docs/hardware-inventory.md`.

## Estado del proyecto

La lectura del DHT11 ya funciona: `src/main.cpp` lee temperatura y humedad cada 2 s y las muestra por el monitor serie (el usuario lo confirmó en el hardware).

Wi-Fi y publicación MQTT (Mosquitto del backend `sensores`) están implementados y compilan; **no probados** en hardware ni contra el broker. Ver [docs/firmware.md](docs/firmware.md). Credenciales en `include/config.h` (no versionado; modelo `include/config.example.h`).

## Agentes y skills

- Agentes en `.claude/agents/`: `iot-developer` (implementa), `iot-architect` (diseña), `electronics-technician` (revisa circuitos) y `technical-writer` (documenta).
- Skills en `.claude/skills/`: `electronics-review` y `update-documentation`.

Wi-Fi y MQTT fueron solicitados por el usuario. No añadir bases de datos, aplicaciones móviles, servicios en la nube, TLS ni otra infraestructura hasta que el usuario lo solicite.