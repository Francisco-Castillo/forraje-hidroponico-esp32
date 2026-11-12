# Kit Starter "plug & play": arquitectura autónoma

Estado: **idea en fase de diseño. No hay código ni hardware nuevo.** Todo lo de este documento es una propuesta salvo que diga "Confirmado". Nada se ha probado físicamente.

Fuentes (ideas del usuario, 2026-11-03): `docs/ideas/Migracion_Backend_MicroSD_Seguridad.md` (decisión vigente), `Anatomia_Kit_Prefabricado_Plug_Play.md` (producto y logística) y los tres planes de negocio `Oportunidades_Agritech_Gdansk*.md` y `Plan_Negocio_Agritech_Gdansk_Completo.md`. Las cifras comerciales de esos planes no están verificadas.

## Decisión

El kit funciona **sin internet**: el ESP32 crea su propia red Wi-Fi, sirve la interfaz web desde una microSD y guarda el histórico en ella. No hay nube ni backend en el dispositivo. El objetivo es no exponer el sistema a ciberataques desde internet.

Spring Boot, Mosquitto y TimescaleDB (proyecto `sensores`) **no se abandonan**. Quedan con dos funciones:

- **Desarrollo:** referencia del modelo de datos y banco de pruebas.
- **Versión "pro"** (futura): opción con servidor, p. ej. clientes B2B. Sin diseñar.

Si las ideas de `docs/ideas/` se contradicen, manda `Migracion_Backend_MicroSD_Seguridad.md`; `Anatomia` y los planes de negocio describen la versión con nube/MQTT.

## Qué se reutiliza

| Pieza actual | Destino en el kit |
|---|---|
| Lectura DHT11 (`src/main.cpp`) y suelo (`src/moisture.cpp`) | Se reutiliza |
| Campos y unidades del contrato MQTT | Base del JSON de la API local y de las columnas del CSV |
| Wi-Fi cliente, MQTT, NTP | No aplican al kit autónomo (sin broker ni internet) |
| Backend `sensores` | Desarrollo y versión pro (ver arriba) |

## Arquitectura propuesta

- **Acceso:** el ESP32 emite su Wi-Fi (modo punto de acceso, AP), con portal cautivo hacia `192.168.4.1`. Opcionalmente se une al Wi-Fi del hogar y responde en `sproutos.local` (mDNS). Cada modo añade complejidad; el primero a probar es el AP.
- **Almacenamiento:** microSD FAT32 de 4–16 GB con la interfaz web estática, recetas JSON y el histórico en CSV.
- **Datos vivos:** últimas lecturas en RAM; la API REST lee de RAM, no de la SD.
- **Dos núcleos:** el núcleo 0 para red y servidor web, el núcleo 1 para sensores y control. Es un objetivo de diseño, no un requisito para el primer prototipo.
- **Energía solar híbrida, relés, LED 24 V, ventiladores y bomba 12 V:** fases posteriores. Hoy no hay actuadores, fuentes ni etapas de potencia seleccionados.
- **Clima exterior:** el navegador del teléfono descargaría el pronóstico por datos móviles y lo enviaría al ESP32 por POST local ("puente teléfono").

## Riesgos y huecos detectados

1. **Pines de la microSD.** El bus SD_MMC de 4 bits del ESP32 usa los GPIO 2, 4, 12, 13, 14 y 15. El DHT11 está en el **GPIO4**: chocaría. Además 2, 12 y 15 son pines "strapping" (influyen en el arranque). Alternativa: un módulo microSD por **SPI** (más simple y suficiente para servir ~2 MB). En la placa del usuario existen P5 (CS), P23 (MOSI), P19 (MISO) y P18 (SCK), sin choque con el GPIO4 ni el GPIO34 (propuesta; **sin conectar ni probar**; P5 debe estar en alto al arrancar). Ver el serigrafiado en `hardware-inventory.md`.
2. **Sin internet no hay hora.** Hoy el timestamp viene de NTP. Para el CSV hace falta un reloj RTC (p. ej. DS3231, **no seleccionado**) o que el navegador del teléfono envíe la hora al ESP32. Los documentos de ideas no lo contemplan.
3. **"Blindaje absoluto" es exagerado.** Sin internet desaparece la exposición remota, pero queda superficie local: contraseña del AP, endpoints sin autenticación, acceso físico a la placa y a la SD. HTTP no cifra; el "JSON encriptado" de las ideas no es cierto sin TLS. Mejora real, no absoluta.
4. **Puente teléfono frágil.** Android e iOS suelen abandonar un Wi-Fi sin internet y usar datos móviles, y entonces el POST a `192.168.4.1` falla. Hay que probarlo en teléfonos reales antes de depender de él.
5. **Sensores.** Las ideas citan DHT22/SHT31; el hardware actual es DHT11 (±2 °C, ±5 % de humedad, valores enteros). Falta decidir el sensor del kit.
6. **Energía solar.** Los umbrales de 12,0 V y 11,5 V son poco fiables en LiFePO4 (curva de voltaje muy plana) y dependen de la carga. El ADC del ESP32 admite hasta 3,3 V, así que haría falta un divisor de tensión. Con 24 V, 12 V y red eléctrica hay que revisar seguridad antes de montar nada, y vender implica marcado CE.
7. **Pérdida de datos en la SD.** Guardar el histórico una vez por hora significa perder hasta 1 h si se corta la luz, y la FAT32 puede corromperse con cortes de energía.
8. **Aprendizaje.** La lógica de negocio pasa de Java a C++ embebido; estimar más esfuerzo del que sugieren los documentos de ideas.
9. **Textos de ideas.** Contienen caracteres rotos ("Gda■sk") por conversión de PDF y los tres planes de negocio se solapan.

## Hardware: placa indicada por el usuario

NodeMCU **ESP32S** de 38 pines, Micro-USB, según el usuario y el listado de venta (chip USB-serie CP2102, 4 MB de flash, 520 KB de SRAM, E/S a 3,3 V). Son datos del listado, **sin verificar físicamente**, y el listado no indica la asignación de pines. La placa no trae ranura microSD: hace falta un módulo aparte. El serigrafiado se leyó de una foto del usuario (2026-11-03) y está en `hardware-inventory.md`. Queda una discrepancia: el pin junto a 5V está rotulado GND, y la página de referencia dice CMD; no usarlo como GND hasta comprobar continuidad con un multímetro (aún no disponible). Revisar con `electronics-review` antes de conectar algo nuevo.

## Fase 0: cultivo manual (en curso de preparación)

Antes de automatizar, aprender a cultivar en casa: ver [fase-0-plan.md](fase-0-plan.md) y la planilla [templates/registro-lotes.xlsx](templates/registro-lotes.xlsx). Estado: plan propuesto; esperando la llegada de la bandeja germinadora y las semillas. Mientras tanto avanzan las tareas que no dependen del cultivo (verificación de hardware, multímetro, pruebas de fallo del firmware, validación comercial).

## Siguiente paso propuesto en firmware (pendiente de aprobación)

Prototipo mínimo en el ESP32: AP propio, servidor web con una página que muestre DHT11 y suelo, **sin SD**. Sirve para probar el flujo del teléfono (riesgo 4) antes de comprar hardware. Requiere un plan aprobado antes de implementarse.
