#include "pump.h"

constexpr uint8_t PUMP_PIN = 26;
constexpr uint32_t PUMP_MAX_ON_MS = 3000;

static bool on = false;
static uint32_t startedAt = 0;

void pumpBegin() {
  pinMode(PUMP_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW);  // apagada al arrancar
}

void pumpStart() {
  digitalWrite(PUMP_PIN, HIGH);
  on = true;
  startedAt = millis();
}

void pumpStop() {
  digitalWrite(PUMP_PIN, LOW);
  on = false;
}

void pumpUpdate() {
  if (on && millis() - startedAt >= PUMP_MAX_ON_MS) {
    pumpStop();
    Serial.println("Bomba: apagada (tiempo maximo)");
  }
}

bool pumpIsOn() { return on; }
