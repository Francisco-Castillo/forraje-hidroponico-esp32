#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <time.h>
#include "config.h"
#include "moisture.h"

constexpr uint8_t DHT_PIN = 4;
constexpr uint32_t TIMEOUT_US = 200;

// Conectividad
constexpr uint32_t BACKOFF_MIN_MS = 1000;
constexpr uint32_t BACKOFF_MAX_MS = 30000;
constexpr time_t MIN_VALID_EPOCH = 1704067200;  // 2024-01-01: el backend descarta fechas anteriores
constexpr size_t MQTT_BUFFER_SIZE = 384;

static WiFiClient wifiClient;
static PubSubClient mqtt(wifiClient);
static char topic[64];
static uint32_t bootId;       // aleatorio en cada arranque
static uint32_t messageCount = 0;

static portMUX_TYPE dhtMux = portMUX_INITIALIZER_UNLOCKED;

enum DhtResult : uint8_t {
  DHT_OK = 0,
  DHT_NO_RESPONSE,   // el sensor no bajo la linea tras el pulso de inicio
  DHT_TIMEOUT_LOW,   // timeout en la respuesta (LOW 80 us)
  DHT_TIMEOUT_HIGH,  // timeout en la respuesta (HIGH 80 us)
  DHT_TIMEOUT_BIT,   // timeout leyendo uno de los 40 bits
  DHT_CHECKSUM,
};

// Mide cuanto dura el nivel actual del pin (en us); 0 si supera el timeout.
static uint32_t pulseLength(bool level) {
  uint32_t start = micros();
  while (digitalRead(DHT_PIN) == level) {
    if (micros() - start > TIMEOUT_US) return 0;
  }
  return micros() - start;
}

static DhtResult readDHT11(float &tempC, float &humidity) {
  uint8_t data[5] = {0, 0, 0, 0, 0};
  DhtResult result = DHT_OK;

  // Pulso de inicio: LOW 18 ms, luego HIGH y pasar a entrada
  pinMode(DHT_PIN, OUTPUT);
  digitalWrite(DHT_PIN, LOW);
  delay(18);

  portENTER_CRITICAL(&dhtMux);
  digitalWrite(DHT_PIN, HIGH);
  delayMicroseconds(30);
  pinMode(DHT_PIN, INPUT_PULLUP);

  // Respuesta del sensor: LOW ~80 us, HIGH ~80 us
  pulseLength(HIGH);  // resto del HIGH de liberacion del bus
  if (digitalRead(DHT_PIN) == HIGH) {
    result = DHT_NO_RESPONSE;
  } else if (pulseLength(LOW) == 0) {
    result = DHT_TIMEOUT_LOW;
  } else if (pulseLength(HIGH) == 0) {
    result = DHT_TIMEOUT_HIGH;
  } else {
    // 40 bits: cada uno es LOW ~50 us y HIGH 26-28 us (0) o ~70 us (1)
    for (int i = 0; i < 40; i++) {
      if (pulseLength(LOW) == 0) { result = DHT_TIMEOUT_BIT; break; }
      uint32_t high = pulseLength(HIGH);
      if (high == 0) { result = DHT_TIMEOUT_BIT; break; }
      data[i / 8] <<= 1;
      if (high > 50) data[i / 8] |= 1;
    }
  }
  portEXIT_CRITICAL(&dhtMux);

  if (result != DHT_OK) return result;
  if ((uint8_t)(data[0] + data[1] + data[2] + data[3]) != data[4]) return DHT_CHECKSUM;

  humidity = data[0] + data[1] / 10.0f;
  tempC = data[2] + data[3] / 10.0f;
  return DHT_OK;
}

// Reintenta Wi-Fi con espera creciente, sin bloquear el loop.
static void maintainWifi() {
  static uint32_t lastAttempt = 0, backoff = BACKOFF_MIN_MS;
  static bool wasConnected = false;

  if (WiFi.status() == WL_CONNECTED) {
    if (!wasConnected) {
      Serial.printf("Wi-Fi conectado, IP %s\n", WiFi.localIP().toString().c_str());
      wasConnected = true;
    }
    backoff = BACKOFF_MIN_MS;
    return;
  }
  if (wasConnected) {
    Serial.println("Wi-Fi desconectado");
    wasConnected = false;
    lastAttempt = millis() - backoff;  // primer reintento inmediato
  }
  if (millis() - lastAttempt < backoff) return;
  lastAttempt = millis();
  Serial.printf("Conectando a Wi-Fi (reintento en %lu ms si falla)\n", (unsigned long)backoff);
  WiFi.disconnect();
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  backoff = min(backoff * 2, BACKOFF_MAX_MS);
}

// Reintenta MQTT con espera creciente; solo si hay Wi-Fi.
static void maintainMqtt() {
  static uint32_t lastAttempt = 0, backoff = BACKOFF_MIN_MS;
  static bool wasConnected = false;

  if (mqtt.connected()) {
    if (!wasConnected) { Serial.println("MQTT conectado"); wasConnected = true; }
    backoff = BACKOFF_MIN_MS;
    return;
  }
  if (wasConnected) {
    Serial.printf("MQTT desconectado (estado %d)\n", mqtt.state());
    wasConnected = false;
  }
  if (WiFi.status() != WL_CONNECTED) return;
  if (lastAttempt != 0 && millis() - lastAttempt < backoff) return;
  lastAttempt = millis();
  Serial.printf("Conectando a MQTT %s:%d\n", MQTT_HOST, MQTT_PORT);
  if (!mqtt.connect(DEVICE_ID, MQTT_USER, MQTT_PASSWORD)) {
    Serial.printf("MQTT fallo (estado %d), reintento en %lu ms\n", mqtt.state(), (unsigned long)backoff);
    backoff = min(backoff * 2, BACKOFF_MAX_MS);
  }
}

// Publica la lectura segun docs/mqtt-contract.md del backend. Devuelve true si se envio.
static bool publishReading(time_t ts, float tempC, float humidity) {
  if (ts < MIN_VALID_EPOCH) {
    Serial.println("Sin hora NTP valida: no se publica");
    return false;
  }
  if (!mqtt.connected()) {
    Serial.println("MQTT no conectado: no se publica");
    return false;
  }
  struct tm tmUtc;
  gmtime_r(&ts, &tmUtc);
  char iso[24];
  strftime(iso, sizeof(iso), "%Y-%m-%dT%H:%M:%SZ", &tmUtc);

  char payload[MQTT_BUFFER_SIZE];
  snprintf(payload, sizeof(payload),
           "{\"deviceId\":\"%s\",\"messageId\":\"%s-%08lx-%lu\",\"timestamp\":\"%s\","
           "\"measurements\":{\"temperatureC\":%.1f,\"relativeHumidityPct\":%.1f}}",
           DEVICE_ID, DEVICE_ID, (unsigned long)bootId, (unsigned long)messageCount, iso, tempC, humidity);

  bool ok = mqtt.publish(topic, payload);
  Serial.printf("Publicacion %s: %s\n", ok ? "OK" : "FALLO", payload);
  if (ok) messageCount++;
  return ok;
}

void setup() {
  Serial.begin(115200);
  pinMode(DHT_PIN, INPUT_PULLUP);
  moistureBegin();

  bootId = esp_random();
  snprintf(topic, sizeof(topic), "fvh/%s/lecturas", DEVICE_ID);
  Serial.printf("Dispositivo %s, topico %s\n", DEVICE_ID, topic);

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  configTime(0, 0, "pool.ntp.org", "time.google.com");  // UTC; sincroniza al haber red
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(MQTT_BUFFER_SIZE);
  mqtt.setSocketTimeout(3);
}

void loop() {
  maintainWifi();
  maintainMqtt();
  mqtt.loop();

  static uint32_t lastRead = 0;
  if (millis() - lastRead < READ_INTERVAL_MS) return;
  lastRead = millis();

  MoistureReading soil = moistureRead();
  Serial.printf("Suelo (sin calibrar): raw=%u  %lu mV\n", soil.raw, (unsigned long)soil.millivolts);

  float t, h;
  DhtResult r = readDHT11(t, h);
  if (r == DHT_OK) {
    Serial.printf("Temperatura: %.1f C  Humedad: %.1f %%\n", t, h);
    publishReading(time(nullptr), t, h);
  } else {
    Serial.println("Temperatura: NaN  Humedad: NaN");
  }
}
