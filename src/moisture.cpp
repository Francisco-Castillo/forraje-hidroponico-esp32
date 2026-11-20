#include "moisture.h"

// GPIO34: solo entrada y ADC1 (el ADC2 no funciona con el Wi-Fi activo).
constexpr uint8_t MOISTURE_PIN = 34;
constexpr uint8_t SAMPLES = 16;  // promedio para reducir el ruido

void moistureBegin() {
  analogSetPinAttenuation(MOISTURE_PIN, ADC_11db);  // rango ~0-3,1 V
}

MoistureReading moistureRead() {
  uint32_t sumRaw = 0, sumMv = 0;
  uint16_t minRaw = 4095, maxRaw = 0;
  for (uint8_t i = 0; i < SAMPLES; i++) {
    uint16_t raw = analogRead(MOISTURE_PIN);
    sumRaw += raw;
    minRaw = min(minRaw, raw);
    maxRaw = max(maxRaw, raw);
    sumMv += analogReadMilliVolts(MOISTURE_PIN);
  }
  uint16_t avgRaw = static_cast<uint16_t>(sumRaw / SAMPLES);
  return {avgRaw, sumMv / SAMPLES, minRaw, maxRaw, avgRaw > 0};
}
