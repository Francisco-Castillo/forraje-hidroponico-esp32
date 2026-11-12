# PLAN ESTRATÉGICO AGRITECH -

# GDA■SK

**Perfil Tecnológico Híbrido: Microvegetales, Automatización e IoT**

Versión 2.0 • Actualizado con Arquitectura Spring Boot / MQTT

1. **Viabilidad del Mercado en Gda**■**sk (Región de Trójmiasto)**

La comercialización de microvegetales en Gda■sk es altamente viable bajo un enfoque estrictamente premium. La ciudad ofrece un ecosistema gastronómico en expansión (con restaurantes galardonados por la guía Michelin como ARCO por Paco Pérez, Eliksir, Fino y Treinta y Tres) y un público local con alto poder adquisitivo concentrado en zonas como Wrzeszcz y Oliwa. Espacios como el _Gda_■_ski_ _Bazar Natury_ sirven como validación directa B2C. La ventaja competitiva clave frente a productores industriales en Polonia radica en la entrega inmediata y en la venta de bandejas vivas.

2. **Líneas de Negocio Tecnológicas Inventadas**

- **Micro-Granjas Automatizadas 'Plug & Play':** Electrodomésticos estéticos e inteligentes para hogares y restaurantes que mitigan los altos costos eléctricos del invierno polaco.
- **Optimización B2B Agritech:** Consultoría y auditoría técnica en eficiencia energética (paneles solares) y sensórica para invernaderos e instalaciones hidropónicas locales.
- **Educación STEM:** Kits educativos y talleres prácticos de agricultura automatizada programada con robótica para colegios internacionales en Trójmiasto.

3. **Profundización Técnica: Micro-Granjas Plug & Play**

El diseño arquitectónico del MVP resuelve las limitaciones de espacio urbano y optimiza el consumo energético en Europa Central:

- **Hardware (ESP32):** Actúa como un cliente periférico dedicado. Lee sensores climáticos críticos (DHT22/SHT31 para temperatura/humedad; ultrasonido para nivel de agua) y acciona relés para la iluminación LED de cultivo (24V) y los extractores de aire de 12V.
- **Energía Solar Híbrida:** Integración de paneles solares compactos colgantes para balcones urbanos y baterías de litio (LiFePO4). El sistema implementa una conmutación automatizada a la red eléctrica tradicional si la carga desciende críticamente debido a la baja radiación invernal.

4. **Arquitectura de Software Desacoplada e IoT**

Para optimizar la memoria limitada del ESP32, se implementa un ecosistema distribuido:

- **Mensajería (Eclipse Mosquitto):** El ESP32 publica telemetría en JSON y se suscribe a tópicos de comandos de forma asíncrona mediante un broker MQTT ligero.
- **Backend Central (Spring Boot):** Centraliza el procesamiento de datos, la persistencia en base de datos, el control de seguridad y la lógica de negocio (reglas de cultivo automatizadas por variedad).
- **Capa de Interfaz de Usuario (UI):** Se desacopla por completo del microcontrolador. Las opciones recomendadas de despliegue según el hito comercial son:

| **Opción UI** | **Tecnología** | **Caso de Uso Ideal** |
| --- | --- | --- |
| **1. Panel Integrado** | Spring Boot + Thymeleaf /HTMX | Fase alfa y MVP funcional en tiempo récordutilizando conocimientos nativos de Java. |
| **2. Low-Code IoT** | ThingsBoard / Grafana | Validación comercial inmediata con clientes B2B.Paneles visuales sin desarrollo frontend. |
| **3. App Desacoplada** | React / Vue.js + WebSockets | Ecosistema premium definitivo paracomercialización masiva y gestión desuscripciones. |

Este documento es para fines exclusivamente informativos y de planificación de negocios. Las especificaciones técnicas e implementaciones de código deben ser validadas en entornos de prueba controlados.
