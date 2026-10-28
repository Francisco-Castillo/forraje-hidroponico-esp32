#include <Arduino.h>

constexpr uint8_t DHT_PIN = 4;
constexpr uint32_t READ_INTERVAL_MS = 2000;
constexpr uint32_t TIMEOUT_US = 200;

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

void setup() {
  Serial.begin(115200);
  pinMode(DHT_PIN, INPUT_PULLUP);
}

void loop() {
  static uint32_t lastRead = 0;
  if (millis() - lastRead < READ_INTERVAL_MS) return;
  lastRead = millis();

  float t, h;
  DhtResult r = readDHT11(t, h);
  if (r == DHT_OK) {
    Serial.printf("Temperatura: %.1f C  Humedad: %.1f %%\n", t, h);
  } else {
    Serial.println("Temperatura: NaN  Humedad: NaN");
  }
}
