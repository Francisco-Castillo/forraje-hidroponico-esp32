// Copiar este archivo a include/config.h y rellenar los valores.
// include/config.h esta en .gitignore: no versionar credenciales.
#pragma once

#define WIFI_SSID      "tu-red-wifi"
#define WIFI_PASSWORD  "tu-clave-wifi"

// IP (o nombre) del PC que ejecuta Mosquitto, accesible desde el ESP32.
// "localhost" NO sirve: seria el propio ESP32.
#define MQTT_HOST      "192.168.1.100"
#define MQTT_PORT      1883
#define MQTT_USER      "usuario-mqtt"
#define MQTT_PASSWORD  "clave-mqtt"

// Formato [a-z0-9-], 1 a 32 caracteres. Tambien es el clientId MQTT.
// El topico de publicacion se deriva: fvh/<DEVICE_ID>/lecturas
#define DEVICE_ID      "esp32-fvh-01"

#define READ_INTERVAL_MS 2000
