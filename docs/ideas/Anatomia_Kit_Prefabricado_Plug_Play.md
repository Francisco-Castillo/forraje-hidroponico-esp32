# Anatomía de la Caja "Plug & Play"

**Especificaciones Técnicas, Logísticas y de Negocio del Kit Listo para Armar (RTA)**

Este documento detalla la arquitectura de producto y el desglose de componentes para el kit prefabricado de microgranjas automatizadas urbanas. Diseñado bajo principios de ingeniería modular y estética escandinava, este modelo optimiza los costos logísticos en el mercado europeo (utilizando dimensiones adaptadas a los casilleros postales de Polonia) mientras asegura una experiencia de usuario fluida sin requerir conocimientos técnicos avanzados.

1. **Contenido de la Caja (BOM Modular)**

<div></div>

1. **Estructura y Chasis RTA:**

- **Perfiles Estructurales:** Listones de madera de haya pre-perforados con insertos metálicos o perfiles de aluminio ranurado (V-Slot 2020) con acabado anodizado negro mate.
- **Estantes de Cultivo:** Bandejas de polímero ABS de grado alimentario, diseñadas con pendientes internas milimétricas para optimizar el flujo y reflujo de agua y evitar estancamientos.
- **Kit de Fijación:** Tornillería métrica estandarizada de acero inoxidable y una herramienta Allen multiuso para que el usuario complete el ensamble en menos de 20 minutos.

1. **El Módulo Central de Control (Cerebro Electrónico):**

- **Caja del Hub Integrado:** Caja plástica sellada contra salpicaduras (IP65) que se encaja a presión en el chasis. Evita que el usuario manipule cables expuestos.
- **Núcleo de Procesamiento:** Microcontrolador ESP32 (o equivalente con Wi-Fi nativo) programado para actuar como cliente IoT ligero.
- **Puertos de Conexión Rápida:** Conectores externos tipo Jack de aviación o puertos modulares impermeables donde se conectan periféricos mediante un sistema 'clic'.

1. **Subsistema de Actuadores e Iluminación:**

- **Barras LED de Espectro Completo:** Tiras de iluminación LED de 24V optimizadas para fotosíntesis de microvegetales, pre-montadas bajo cada estante con difusores de policarbonato.
- **Ventilación Dinámica:** Microventiladores ultrasilenciosos de 12V (tecnología MagLev) integrados estratégicamente para romper la capa límite de humedad y prevenir hongos (moho blanco).
- **Bomba Hidropónica:** Mini bomba sumergible de bajo consumo (12V DC) con conector rápido de tubería flexible.

Este documento es para fines informativos y de desarrollo de negocio. AI responses may include mistakes. Página 1 de 2

1. **Insumos y Starter Pack:**

- **Almohadillas de Semillas (Pads):** Tres bandejas de cultivo biodegradables basadas en fibra de coco

    1. celulosa con densidades de semilla pre-calculadas (Rábano, Girasol, Amaranto).

2. **Especificaciones Logísticas y Distribución**

El producto se almacena y transporta desarmado en un formato de caja plana (Flat-pack). Esto permite reducir los costos de almacenamiento un 70% y utilizar redes de distribución automatizadas.

**Parámetro Logístico** **Especificación en Kit de Cocina / Sobremesa**

Dimensiones de la Caja 60 cm x 40 cm x 15 cm (Optimizado para Gabaryt C de InPost Polonia)

Peso Total de la Caja 4.5 kg a 5.2 kg (Fácil de cargar por una sola persona)

Tiempo de Ensamble 15 a 20 minutos utilizando únicamente la herramienta incluida

estimado

Cunas de cartón corrugado reciclado de alta densidad (cero plásticos de

Protección Interna un solo uso)

3. **Flujo de Trabajo e Integración de Software Desacoplado**

Para garantizar que el hardware mantenga un bajo consumo de memoria y máxima estabilidad, la lógica se distribuye completamente en un entorno en la nube o servidor local.

- **Paso 1: Montaje y Conexión Eléctrica.** El cliente une el chasis, coloca las bandejas y conecta los cables rápidos al hub central. Enciende el equipo conectándolo a la corriente.
- **Paso 2: Vinculación Wi-Fi (Provisionamiento).** El ESP32 inicia en modo Access Point temporal. El usuario escanea el código QR del manual, accede a una interfaz básica y guarda las credenciales del Wi-Fi de su hogar.
- **Paso 3: Suscripción y Publicación MQTT.** El ESP32 se conecta al broker **Eclipse Mosquitto** y comienza a publicar datos de sensores (JSON con temperatura, humedad, nivel de agua) en un canal dedicado, mientras se suscribe al canal de comandos.
- **Paso 4: Orquestación en Backend.** Tu servidor **Spring Boot** procesa las telemetrías del MQTT, gestiona el estado del ciclo (ej. día 4 de crecimiento de rábano) y envía de vuelta las directivas exactas (ej. apagar luces a las 22:00, encender bomba por 3 minutos).
- **Paso 5: Visualización de Usuario.** El usuario final interactúa con la interfaz web hospedada en el backend (Thymeleaf/HTMX o React) para monitorear el crecimiento, recibir alertas de rellenado de agua y comprar nuevas almohadillas de semillas.

Este documento es para fines informativos y de desarrollo de negocio. AI responses may include mistakes. Página 2 de 2
