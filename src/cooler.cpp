#include "cooler.h"

constexpr uint8_t COOLER_PIN = 17;

static bool on = false;

void coolerBegin() {
  pinMode(COOLER_PIN, OUTPUT);
  digitalWrite(COOLER_PIN, LOW);  // apagado al arrancar
}

void coolerOn() {
  digitalWrite(COOLER_PIN, HIGH);
  on = true;
}

void coolerOff() {
  digitalWrite(COOLER_PIN, LOW);
  on = false;
}

bool coolerIsOn() { return on; }
