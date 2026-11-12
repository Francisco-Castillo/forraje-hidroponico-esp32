# PLAN DE NEGOCIOS AGRITECH: MICROVEGETALES EN GDANSK

**Perfil Profesional Integrado:** Paneles Solares, Software (Spring Boot, MQTT) y Electrónica (Arduino/ESP32)

_Análisis de Viabilidad, Canales de Mercado y Arquitectura IoT Desacoplada_

1. **Viabilidad Comercial de Microvegetales en Gda**■**sk, Polonia**

El cultivo de microvegetales es un negocio rentable debido a sus ciclos cortos (7-14 días), alta densidad por metro cuadrado en sistemas verticales y bajo costo inicial en insumos básicos. En Gda■sk y la región de Trójmiasto (Sopot y Gdynia), la viabilidad comercial es altamente favorable bajo un enfoque de nicho premium, apalancado por las condiciones locales:

- **Escena Gastronómica de Alta Gama:** La ciudad cuenta con una creciente presencia de restaurantes con estrellas o menciones Michelin (como ARCO by Paco Pérez, Eliksir, Fino, Treinta y Tres) concentrados en zonas turísticas como el Centro Histórico (G■ówne Miasto) y la Isla de Graneros (Wyspa Spichrzów). Estos establecimientos demandan microvegetales exóticos y consistencia visual.
- **Cultura Ecológica Premium:** Espacios de comercialización de proximidad como el Gda■ski Bazar Natury en Wrzeszcz validan el fuerte interés de la clase media-alta local por productos de cercanía y saludables.
- **Factor Climático como Oportunidad:** El invierno polaco largo y con pocas horas de sol reduce a cero la producción local tradicional exterior, lo que otorga una enorme ventaja competitiva a las granjas indoor automatizadas capaces de ofrecer producto fresco los 365 días del año.
- **Desafíos Clave:** La competencia de macro-granjas polacas nacionales (ej. Listny Cud) obliga a competir por frescura (entrega viva) y no por precio. Asimismo, es obligatorio considerar las gestiones regulatorias alimentarias locales ante el cuerpo oficial de inspección sanitaria (Sanepid).

2. **Diversificación de Oportunidades Basadas en Tecnología** **(Perfil Híbrido)**

En lugar de competir en volumen agrícola, tu experiencia en software, electrónica y energía solar te posiciona en el segmento de mayor margen de la cadena de valor: los proveedores de tecnología e infraestructura resiliente.

| **Línea de Negocio** | **InversiónInicial** | **Público Objetivo** | **Complejidad de Entrada** |
| --- | --- | --- | --- |

| **1. Micro-Granjas AutomatizadasPlug & Play:** Venta de mueblesestéticos y automatizados con unmodelo recurrente de insumos(Pads de semillas). | Media | Restaurantes premium urbanos yamantes del home-growing. | Baja-Media (Alta escalabilidadcomercial). |
| --- | --- | --- | --- |
| **2. Consultoría B2B eIntegración Agritech:**Optimización energética einstalación de sensores eninvernaderos comercialesexistentes. | Baja | Productores medianos y granjashidropónicas locales. | Alta (Requiere redes decontacto locales). |
| **3. Kits Educativos y TalleresSTEM:** Programas prácticos yhardware educativo combinandoArduino, robótica básica ybotánica. | Baja | Colegios internacionales privadosen Trójmiasto. | Baja (El inglés es nativo eneste nicho). |

3. **Foco Técnico: Micro-Granjas Automatizadas Plug & Play**

Esta solución aborda directamente el costo energético en Polonia y el limitado espacio habitacional, permitiendo un flujo de ingresos recurrentes mediante suscripciones de bandejas sembradas.

### Hardware y Eficiencia Energética

- **Unidad de Control (ESP32):** Se selecciona sobre Arduino clásico por su conectividad Wi-Fi integrada, bajo costo y memoria adecuada para flujos de datos puros utilizando la librería PubSubClient.
- **Sensores y Actuadores:** Monitoreo de temperatura y humedad crítica (DHT22/SHT31) para prevención de hongos, sensores de nivel de agua en el tanque de riego, relés para control de ciclos lumínicos LED de cultivo (24V) y ventiladores de extracción de 12V silenciosos.
- **Arquitectura Solar Híbrida Balcón/Red:** Incorporación de paneles solares compactos (100W-200W) diseñados para estructuras colgantes seguras en balcones de departamentos urbanos, conectados a una batería de litio (LiFePO4). El firmware conmuta mediante relés automáticos a la red eléctrica si la batería se agota debido al déficit solar en el invierno polaco, reduciendo los picos en la factura eléctrica.

4. **Arquitectura de Software e Interfaz de Usuario Desacoplada**

Al contar con un stack existente en **Spring Boot y Eclipse Mosquitto (MQTT)**, la memoria limitada del ESP32 deja de ser un problema. El ESP32 se comporta como un nodo de hardware puro que publica lecturas de sensores y se suscribe a tópicos de comandos entrantes.

| **Tipo de Interfaz** | **Infraestructura / Ubicación** | **Ventajas Técnicas y Comerciales** |
| --- | --- | --- |

| **1. Panel Integrado(Thymeleaf + HTMX)** | Servidor backend de SpringBoot. | Desarrollo ágil monorepo aprovechando elconocimiento de Java. Con HTMX y WebSockets selogran actualizaciones en tiempo real fluidas sinframeworks pesados de JS. Ideal para fases MVP. |
| --- | --- | --- |
| **2. Dashboard Low-Code(ThingsBoard / Grafana)** | Despliegue local en la mismainstancia del broker MQTT. | Cero código frontend requerido. Permite arrastrarwidgets analíticos robustos, medidores de nivel deagua y alarmas automáticas por correo electrónico demanera inmediata. Ideal para validación B2B. |
| **3. Aplicación Web Pura(React / Vue.js)** | Desacoplado de formaindependiente (ej. Vercel /Netlify). | Separación total de responsabilidades. Consume APIsREST y WebSockets del backend en Spring Boot.Ofrece la mejor experiencia UX móvil y de escritoriopara el usuario final. Escalable para un producto deconsumo masivo. |

### Flujo de Datos del Sistema Integrado

La comunicación sigue el patrón desacoplado estándar de la industria:

1. El **ESP32** lee las variables físicas del microclima y las envía estructuradas en formato JSON hacia el broker **Mosquitto**.
2. El backend de **Spring Boot** actúa como el orquestador principal: procesa los mensajes entrantes de Mosquitto, audita los datos históricos en la base de datos, evalúa reglas de negocio y retransmite los estados hacia el frontend.
3. La **Interfaz de Usuario (UI)** elegida consume la información mediante WebSockets de Spring Boot para renderizado dinámico en tiempo real y realiza peticiones HTTP REST para configuraciones de usuario (como el cambio de modos automatizados de cultivo).

<div></div>

5. **Ruta Crítica de Validación Local**

Para iniciar de forma ágil en el mercado de Pomerania, se define el siguiente mapa de ruta:

1. **Fase de Prototipado Rápido (MVP):** Ensamblar una estructura modular simple utilizando una base existente (ej. estantería metálica compacta), tiras LED fijas de espectro completo y un ESP32 en placa de desarrollo con el firmware base de MQTT.
2. **Pruebas de Estrés Térmico y Lumínico:** Operar el sistema en un entorno residencial real de Gda■sk durante el invierno. Calcular el consumo real de Kilovatios-hora (kWh) para estructurar el argumento de venta de ahorro energético frente a la competencia.
3. **Validación de Campo Comercial:** Ofrecer el prototipo estético bajo la modalidad de comodato (prueba gratuita de 30 días) en una cafetería local con alto tráfico en Wrzeszcz o ■ródmie■cie, recopilando retroalimentación directa sobre la facilidad de uso y el impacto estético en los clientes.
