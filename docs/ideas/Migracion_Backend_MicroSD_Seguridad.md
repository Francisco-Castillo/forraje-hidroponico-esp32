# SPROUTOS: Migración a Arquitectura Autónoma de Borde

Manual técnico de ingeniería para la desvinculación de la nube, integración de Micro SD y blindaje perimetral absoluto contra ciberataques.

1. **Justificación y Cambio de Paradigma Arquitectónico**

Para garantizar la privacidad absoluta en entornos domésticos y gastronómicos comerciales en Gda■sk, el diseño de **SPROUTOS** migra hacia un entorno de ejecución local aislado (**Air-Gapped Edge Computing**). Se elimina de raíz la dependencia del internet exterior y de infraestructuras en la nube tradicionales.

**Migración Crítica de Software:** El backend original programado en Java Spring Boot con Eclipse Mosquitto (MQTT) se descarta en el dispositivo embebido. Spring Boot requiere una Máquina Virtual de Java (JVM) y recursos de memoria RAM (gigabytes) inviables para un microcontrolador. En su lugar, toda la lógica de negocio, enrutamiento de red y APIs se reescribe de forma nativa en **C++ embebido** utilizando programación asincrónica multiprocesamiento dentro del ESP32.

2. **Especificaciones de la Tarjeta Micro SD y Rendimiento de** **Hardware**

La tarjeta Micro SD externa actúa como el disco duro de estado sólido del dispositivo, asumiendo tres roles críticos:

    - **Capacidad Óptima:** Tarjetas de **4 GB a 16 GB**. Tamaños superiores (64 GB+) son contraproducentes debido a los tiempos excesivos de indexación en microcontroladores.
    - **Sistema de Archivos:** Formateo obligatorio en **FAT32** para compatibilidad nativa con la librería del sistema de archivos del ESP32.
    - **Almacenamiento Interno:** Aloja la interfaz web completa (HTML/CSS/JS estáticos compilados en producción, de ~2 MB), las recetas de semillas en formato plano JSON (1 KB c/u) y los históricos de métricas de cultivo en archivos (.csv).

### Mecanismo de Optimización y Tiempos de Respuesta:

Los tiempos de respuesta del sistema ante las peticiones del usuario se sitúan en un rango imperceptible de **50** **a 150 milisegundos** gracias a dos decisiones de ingeniería:

    1. **Bus de Hardware SD\_MMC (4 bits):** Se descarta la conexión por interfaz SPI convencional (1 bit). El bus dedicado SD\_MMC utiliza líneas de transmisión en paralelo, permitiendo transferencias masivas de datos y la carga instantánea de la interfaz web en el navegador del teléfono del usuario.
    2. **Métricas Almacenadas en Memoria Caché (RAM):** Los datos dinámicos provenientes de los sensores (Humedad, Temperatura, Voltaje de Batería) residen de forma permanente en la RAM estática del ESP32. Las llamadas REST a la API leen directamente de la memoria RAM, eliminando el desgaste físico y los

SPROUTOS — Arquitectura de Software Autónoma y Ciberseguridad

tiempos de latencia asociados a la lectura de la tarjeta Micro SD. La tarjeta externa solo es accedida por el sistema durante la inicialización de hardware o para la persistencia del archivo histórico una vez por hora.

3. **Gestión del Rendimiento y Arquitectura Dual-Core**

El microprocesador de dos núcleos Tensilica Xtensa de 32 bits (operando a 240 MHz) se configura bajo un esquema de asimetría de tareas estrictamente balanceada para garantizar que el servidor web local no interfiera con el control vital del hardware:

| **Núcleo / Core** | **Foco de Procesamiento Asignado** | **Funciones Técnicas Específicas** |
| --- | --- | --- |
| **Núcleo 0 (Core 0)** | Comunicaciones de Red yConectividad Local | • Ejecución del Servidor Web Asincrónico.• Despacho de paquetes desde la Micro SD.• Gestión de peticiones REST entrantes. |
| **Núcleo 1 (Core 1)** | Lógica Agrícola de Borde e Ingenieríade Control | • Monitoreo de sensores DHT22 cada 2 segundos.• Algoritmos de control híbrido del Panel Solar.• Conmutación analógica de relés y Pantalla OLED. |

4. **Control Solar Híbrido Desconectado**

El ESP32 asume la gobernanza total del sistema de energía sin servidores externos. Monitorea mediante un pin analógico el voltaje en tiempo real del banco de baterías de Litio (LiFePO4) conectado al panel flexible del balcón. El algoritmo ejecuta la conmutación de fuentes basándose en parámetros locales:

    - **Modo Solar Activo (\>12.0V):** El ESP32 conmuta el relé de estado sólido hacia la salida CC de la batería, alimentando las barras de iluminación LED de cultivo y ventilación con energía 100% limpia y renovable.
    - **Redundancia Local (\<11.5V):** Ante la ausencia prolongada de radiación solar en los meses de invierno en Gda■sk, el microcontrolador desactiva el relé instantáneamente, conmutando el circuito de vuelta hacia la fuente de poder regulada conectada a la toma eléctrica doméstica de la pared. El ciclo biológico del microvegetal se mantiene intacto de forma reactiva y segura.

5. **Solución de Acceso y Dirección IP Local (Portal Cautivo y** **mDNS)**

Para erradicar la fricción técnica de los usuarios finales, el acceso local al panel de administración implementa un sistema automatizado de dos etapas:

    1. **Modo Punto de Acceso (AP) y Portal Cautivo Autónomo:** Al encenderse, el mueble emite su propia red Wi-Fi encriptada local (ej: _SPROUTOS\_WiFi_). Al conectarse desde cualquier teléfono móvil, el ESP32 intercepta las peticiones de DNS mediante un servidor interno redireccionando todo el tráfico hacia su IP estática por defecto (**192.168.4.1**). Esto hace que se despliegue de manera automática la interfaz web en la pantalla del usuario en formato de ventana emergente, idéntico al proceso de autenticación de una red hotelera o corporativa.
    2. **mDNS (Multicast DNS) Residencial:** Si el usuario opta por enlazar el dispositivo a la red Wi-Fi interna de su hogar para mantener su conectividad móvil activa de forma simultánea, el mueble inicia el servicio mDNS embebido. El usuario ya no requiere conocer o ingresar la dirección IP numérica asignada

SPROUTOS — Arquitectura de Software Autónoma y Ciberseguridad

dinámicamente por el módem-router; le basta con digitar en su navegador la URL nemotécnica amigable **http://sproutos.local**.

6. **Captura de Datos Meteorológicos con Aislamiento (El** **Enfoque Puente Teléfono)**

Dado que el dispositivo opera bajo una condición estricta de aislamiento perimetral físico (sin salida de red hacia el router exterior para blindarse contra ataques cibernéticos), no posee permisos directos para realizar peticiones HTTP hacia servicios de meteorología externos en la nube.

La arquitectura resuelve la integración del pronóstico climático de Gda■sk delegando la conexión al navegador web del teléfono del usuario a través del concepto de **Puente de Red Seguro**. Cuando el usuario accede a la interfaz local, el código JavaScript de la aplicación (ejecutándose en el cliente) descarga los datos de la API del clima utilizando la red de datos móviles (4G/5G) del propio teléfono. Tras estructurar la predicción de radiación, el mismo navegador envía un paquete JSON local encriptado mediante un método POST local hacia el endpoint interno del ESP32. El mueble adquiere la previsión del clima necesaria para programar sus estrategias de eficiencia energética sin comprometer jamás su aislamiento con el exterior.
